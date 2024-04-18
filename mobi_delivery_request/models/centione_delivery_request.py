# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'
    _order = 'date_start desc,id desc'

    delivery_request_id = fields.Many2one('centione.delivery.request', tracking=True)

    def button_approved(self):
        res = super(PurchaseRequest, self).button_approved()
        for rec in self:
            if rec.delivery_request_id:
                delivery = self.env['centione.delivery.request'].search([
                    ('id', '=', rec.delivery_request_id.id)])
                delivery_line = self.env['centione.delivery.request.line'].search([
                    ('request_id', '=', delivery.id), ('product_id', '=', rec.line_ids[0].product_id.id)
                ])
                delivery_line.is_pr = True
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    delivery_request_id = fields.Many2one('centione.delivery.request', tracking=True)
    purchase_requests = fields.Char('Purchase Requests', readonly=True, tracking=True)
    delivery_ids = fields.Many2many(comodel_name="centione.delivery.request", readonly=True)
    is_delivery = fields.Boolean(default=False, compute='_compute_delivery')
    delivery_request_line_id = fields.Integer()
    initial_mrp_line_id = fields.Integer()

    @api.depends('delivery_ids')
    def _compute_delivery(self):
        for rec in self:
            if rec.delivery_ids:
                rec.is_delivery = True


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    delivery_request_id = fields.Many2one('centione.delivery.request',
                                          related='request_id.delivery_request_id')


class ProductCategoryInherit(models.Model):
    _inherit = "product.category"

    manager_id = fields.Many2many('res.users', string='Manager', tracking=True)


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    product_department_ids = fields.Many2many('hr.department', string='Department')
    picking_type_first_id = fields.Many2one(comodel_name="stock.picking.type", string="First Picking Type")
    picking_type_second_id = fields.Many2one(comodel_name="stock.picking.type", string="Second Picking Type")
    picking_type_purchase_id = fields.Many2one(comodel_name="stock.picking.type", string="Purchase Picking Type")
    delivery_location_id = fields.Many2one('stock.location', string='Source Location')
    delivery_location_dest_id = fields.Many2one('stock.location', string='Destination Location')


class CentioneDeliveryRequest(models.Model):
    _name = "centione.delivery.request"
    _description = 'Delivery Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id.company_id', 'in',
             [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1).id

    name = fields.Char(readonly=True, tracking=True)
    description = fields.Text(string="Description", tracking=True)
    employee_id = fields.Many2one('hr.employee', required=True, string="Employee",
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)]),
                                  tracking=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id, tracking=True)
    delivery_lines_ids = fields.One2many('centione.delivery.request.line', 'request_id',
                                         string='Delivery Request Lines', tracking=True)
    current_user_id = fields.Many2one(comodel_name="res.users", string="Current User", required=False,
                                      default=lambda self: self.env.uid, tracking=True)
    # analytic_account_id = fields.Many2one(related='employee_id.department_id.analytic_account_id', tracking=True)
    warehouse_id = fields.Many2one('stock.warehouse', "Warehouse", tracking=True)
    is_approved = fields.Boolean(default=False, compute='approve1_checked')
    is_approved2 = fields.Boolean(default=False)
    is_internal = fields.Boolean(string="Internal Delivery")
    internal_approval_id = fields.Many2one(comodel_name="res.users", string="Approval", tracking=True)
    project_id = fields.Many2one(comodel_name="project.project", string="Project", tracking=True)
    reason = fields.Text(tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('first_approval', 'PM Approval'),
        ('second_approval', '2nd Approval'),
        ('third_approval', '3rd Approval'),
        ('receive', 'Receive'),
        ('finished', 'Finished'),
        ('cancel', 'Cancel')], default='draft', copy=False, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    picking_type_id = fields.Many2one('stock.picking.type',
                                      string='Operation Type', domain="[('code', '=', 'outgoing')]", required=True,
                                      default=_get_default_picking_type, tracking=True)
    user_id = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', tracking=True)

    def transfers_count(self):
        for rec in self:
            rec.transfer_count = self.env['stock.picking'].search_count(
                [('origin', '=', rec.name)])

    transfer_count = fields.Integer(compute="transfers_count", readonly=True, string="Transfers")
    location_id = fields.Many2one('stock.location', "Source Location", domain="[('usage', '=', 'internal')]",
                                  required=True, tracking=True)
    account_analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Analytic Account",
                                                  tracking=True)

    def cancel_request(self):
        for delivery_line in self.delivery_lines_ids:
            delivery_line.cancel_line()
        return self.write({'state': 'cancel'})

    def delivery_transfers_action(self):
        return {
            'name': _('Transfers'),
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'domain': [('origin', '=', self.name)],
        }

    def purchase_req_count(self):
        for rec in self:
            rec.delivery_purchase_count = self.env['centione.purchase.request'].search_count(
                [('origin', '=', rec.name)])

    delivery_purchase_count = fields.Integer(compute="purchase_req_count", readonly=True, string="Purchase Requests")
    purchase_requests_count = fields.Integer(string="Purchase Requests Count", required=False,
                                             compute='compute_purchase_requests_count')
    purchase_order_count = fields.Integer(string="Purchase Requests Count", required=False,
                                          compute='compute_purchase_order_count')

    def action_open_purchase_requests(self):
        for rec in self:
            ids = self.env['purchase.request'].search([('delivery_request_id', '=', rec.id)]).ids
            context = dict(self.env.context or {})
            context.update({'default_delivery_request_id': rec.id})
            return {
                'name': 'Purchase Requests',
                'view_mode': 'tree,form',
                'res_model': 'purchase.request',
                'context': context,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', ids)],
            }

    def action_open_purchase_orders(self):
        for rec in self:
            ids = self.env['purchase.order'].search(
                [('delivery_ids', 'in', rec.id),
                 ('state', 'in', ['confirm', 'done'])]).ids
            context = dict(self.env.context or {})
            context.update({'default_delivery_request_id': rec.id})
            return {
                'name': 'Purchase Orders',
                'view_mode': 'tree,form',
                'res_model': 'purchase.order',
                'context': context,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', ids)],
            }

    def compute_purchase_requests_count(self):
        for rec in self:
            rec.purchase_requests_count = len(self.env['purchase.request'].search(
                [('delivery_request_id', '=', rec.id)]))

    def compute_purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = len(self.env['purchase.order'].search(
                [('delivery_ids', 'in', rec.id),
                 ('state', 'in', ['confirm', 'done'])]))

    def delivery_purchases_action(self):
        return {
            'name': _('Purchase Requests'),
            'view_mode': 'tree,form',
            'res_model': 'centione.purchase.request',
            'type': 'ir.actions.act_window',
            'domain': [('origin', '=', self.name)],
        }

    def approve1_checked(self):
        for rec in self:
            rec.is_approved = rec.is_approved
            if rec.employee_id.coach_id.user_id.id == rec.env.uid:
                rec.is_approved = True

    def submit_request(self):
        if self.delivery_lines_ids:
            if self.is_internal:
                for delivery_line in self.delivery_lines_ids:
                    delivery_line.state = 'first_approved_by_manager'
                return self.write({'state': 'first_approval'})
            else:
                for delivery_line in self.delivery_lines_ids:
                    delivery_line.state = 'first_approved_by_manager'
                return self.write({'state': 'first_approval'})
        else:
            raise ValidationError("Sorry,  You Must Enter Delivery Request Lines First")

    def back_to_pm_approval(self):
        return self.write({'state': 'first_approval'})

    def finish_btn(self):
        return self.write({'state': 'finished'})

    def back_to_second_approve(self):
        return self.write({'state': 'second_approval'})

    def first_approve(self):
        if self.delivery_lines_ids:
            for delivery_line in self.delivery_lines_ids:
                delivery_line.state = 'approved_by_manager'
            return self.write({'state': 'second_approval'})
        else:
            raise ValidationError("Sorry,  You Must Enter Delivery Request Lines First")

    def second_approve(self):
        return self.write({'state': 'third_approval'})

    def third_approve(self):
        last_id = self.env['stock.picking'].search([])[-1].id if len(self.env['stock.picking'].search([])) else 0
        for rec in self:
            item_vals = {
                'id': last_id + 1,
                'partner_id': rec.partner_id.id,
                'transfer_bool': True,
                'picking_type_id': rec.picking_type_id.id,
                'location_id': rec.picking_type_id.default_location_src_id.id,
                'location_dest_id': rec.project_id.analytic_account_id.wip_location_id.id if rec.project_id.state == 'in_progres' else rec.project_id.analytic_account_id.cost_location_id.id,
                'origin': rec.name,
            }
            sale_order_obj = self.env['stock.picking'].create(item_vals)
            for record in rec.delivery_lines_ids:
                last_line_id = record.env['stock.move'].search([])[-1].id if len(
                    record.env['stock.move'].search([])) else 0
                lines = {
                    'id': last_line_id + 1,
                    'picking_id': sale_order_obj.id,
                    'location_id': rec.picking_type_id.default_location_src_id.id,
                    'location_dest_id': rec.project_id.analytic_account_id.wip_location_id.id if rec.project_id.state == 'in_progres' else rec.project_id.analytic_account_id.cost_location_id.id,
                    'product_id': record.product_id.id,
                    'name': record.product_id.name,
                    'product_uom_qty': record.qty,
                    'product_uom': record.uom_id.id,
                }
                self.env['stock.move'].create(lines)
            sale_order_obj.action_assign()
        return self.write({'state': 'receive'})

    def first_internal_approve(self):
        if self.delivery_lines_ids:
            for delivery_line in self.delivery_lines_ids:
                delivery_line.state = 'approved_by_manager'
            return self.write({'state': 'second_approval'})
        else:
            raise ValidationError("Sorry,  You Must Enter Delivery Request Lines First")

    def purchase_request(self):
        for delivery_line in self.delivery_lines_ids:
            delivery_line.state = 'received'
        return self.write({'state': 'purchase_request'})

    def purchase_order(self):
        return self.write({'state': 'purchase_order'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('centione.delivery.request')
        return super(CentioneDeliveryRequest, self).create(vals)


class CentioneDeliveryRequestLine(models.Model):
    _name = "centione.delivery.request.line"
    _description = 'Centione Delivery Request Line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    product_id = fields.Many2one('product.product', "Product", required=True, tracking=True)

    def _check_manager(self):
        for record in self:
            if record.env.user.id in record.product_id.categ_id.manager_id.ids:
                record.is_manager = True
            else:
                record.is_manager = False
        return {}

    current_user_id = fields.Many2one(comodel_name="res.users", string="Current User", required=False,
                                      default=lambda self: self.env.uid, tracking=True)
    qty = fields.Float(required=True, tracking=True)
    notes = fields.Text()
    uom_id = fields.Many2one('uom.uom', tracking=True)
    request_id = fields.Many2one('centione.delivery.request')
    is_manager = fields.Boolean(compute=_check_manager)
    received_amount = fields.Float('Recived Amount', tracking=True)
    requested_amount = fields.Float('Requested Amount', default=0.0, tracking=True)
    broker_warehouse = fields.Many2one('stock.location', "Broker Warehouse")
    picking_ids = fields.One2many(comodel_name="stock.picking", inverse_name="delivery_request_line_id", string="",
                                  required=False, )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('first_approved_by_manager', 'First Approval by Employee managers'),
        ('approved_by_manager', 'Second Approval by Category Products managers'),
        ('warehouse_review', 'Warehouse_review'),
        ('received', 'Received'),
        ('purchase_request', 'Purchase Request'),
        ('cancel', 'Cancel'),
        ('requested', 'Requested')
    ], default='draft', readonly=True, tracking=True)
    is_service = fields.Boolean("Is Service", default=False)
    is_approved2 = fields.Boolean()
    on_hand = fields.Float(string='On Hand', compute='compute_on_hand', tracking=True)
    is_received = fields.Boolean(default=False, tracking=True)
    is_pr = fields.Boolean(default=False, tracking=True)
    product_type = fields.Selection(related="product_id.detailed_type", tracking=True)
    transfer_qty_done = fields.Float(string="Done", tracking=True)
    difference = fields.Float(string="Difference", compute='_compute_difference', tracking=True)
    received_qty = fields.Float(string="Received", tracking=True)
    rfq = fields.Float(string="rfq", readonly=True, tracking=True)

    @api.depends('received_qty', 'qty')
    def _compute_difference(self):
        for line in self:
            line.difference = line.qty - line.received_qty

    def action_open_line(self):
        for rec in self:
            return {
                'name': 'Check History',
                'view_mode': 'form',
                'res_model': 'centione.delivery.request.line',
                'type': 'ir.actions.act_window',
                'res_id': rec.id,
                'target': 'new',
                'views': [(self.env.ref(
                    'mobi_delivery_request.id_centione_delivery_request_line_form').id, 'form')],
            }

    @api.depends('product_id', 'request_id.picking_type_id')
    def compute_on_hand(self):
        stock_quant_obj = self.env['stock.quant'].search(
            [('product_id', '=', self.product_id.id),
             ('location_id', '=', self.request_id.picking_type_id.default_location_src_id.id)])
        on_hand = 0
        for obj in stock_quant_obj:
            on_hand += obj.quantity
        self.on_hand = on_hand

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {
            'domain': {'uom_id': [('id', 'in', [])]}
        }
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            res['domain']['uom_id'] = [('category_id', '=', self.product_id.uom_id.category_id.id)]
        if self.product_id.type == 'service':
            self.is_service = True
        else:
            self.is_service = False
        return res

    def approve_line(self):
        if self.env.uid in self.product_id.categ_id.manager_id.ids:
            self.write({'is_approved2': True})
        else:
            raise ValidationError("Sorry, You Can\'t approve ,You are not the manager of product category")

    def cancel_line(self):
        self.write({'state': 'cancel', 'is_approved2': True})

    def receive_line_function(self):
        if self.qty == self.received_amount:
            self.write({'state': 'received'})

    def create_centione_purchase_action(self):
        return {
            'name': _('Purchase Requests'),
            'view_mode': 'form',
            'res_model': 'purchase.request',
            'type': 'ir.actions.act_window',
            'context': {
                'default_delivery_request_id': self.request_id.id,
            },
            'target': 'new',
        }


class ReceiveConfirmation(models.TransientModel):
    _name = 'receive.confirmation'
    _description = 'Receive Confirmation'

    received_amount = fields.Float('Quantity2222')

    def confirm_transferring(self):
        self.ensure_one()
        delivery_request_line = self.env['centione.delivery.request.line'].browse(self.env.context.get('active_id'))
        picking = self.env['stock.picking'].search([('origin', '=', delivery_request_line.request_id.name)], limit=1)
        if self.received_amount > delivery_request_line.qty:
            raise ValidationError(
                "Sorry, That Is Invalid Quantity : Received Quantity Cannot Exceed Requested Quantity")
        else:
            delivery_request_line.received_qty = self.received_amount
            delivery_request_line.is_received = True
            for operation in picking.move_line_ids_without_package:
                if delivery_request_line.product_id == operation.product_id:
                    operation.received_qty = self.received_amount


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_id = fields.Many2one('centione.delivery.request')
    delivery_request_line_id = fields.Many2one('centione.delivery.request.line', string="Delivery Request Line")
    transfer_bool = fields.Boolean()

    def button_validate(self):
        result = super(StockPicking, self).button_validate()
        for rec in self:
            if rec.transfer_bool:
                delivery_request = self.env['centione.delivery.request'].search([
                    ('name', '=', rec.origin)])
                for line in delivery_request.delivery_lines_ids:
                    for operation in rec.move_line_ids_without_package:
                        if line.product_id == operation.product_id:
                            line.transfer_qty_done = operation.qty_done
        return result


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    received_qty = fields.Float()
