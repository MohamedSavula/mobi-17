# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)
_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('base_approved', 'Manager Approved'),
    ('1st_approved', '1st Approved'),
    ('2st_approved', '2nd Approved'),
    ('3st_approved', '3rd Approved'),
    ('4st_approved', '4th Approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancel', 'Canceled'),
    ('done', 'Done')
]


class CategoryDepartment(models.Model):
    _name = 'category.department'

    name = fields.Char(string="Department", required=True)
    product_category_ids = fields.Many2many(comodel_name="product.category", relation="category_department_relation",
                                            column1="column1", column2="column2")
    # approvals
    approve_1st_approver_ids = fields.Many2many(comodel_name="res.users", relation="approve_1st_approver_ids",
                                                column1="column1", column2="column2", string="1st Approved")
    approve_2st_approver_ids = fields.Many2many(comodel_name="res.users", relation="approve_2st_approver_ids",
                                                column1="column1", column2="column2", string="2nd Approved")
    approve_3st_approver_ids = fields.Many2many(comodel_name="res.users", relation="approve_3st_approver_ids",
                                                column1="column1", column2="column2", string="3rd Approved")
    approve_4st_approver_ids = fields.Many2many(comodel_name="res.users", relation="approve_4st_approver_ids",
                                                column1="column1", column2="column2", string="4th Approved")
    approve_5st_approver_ids = fields.Many2many(comodel_name="res.users", relation="approve_5st_approver_ids",
                                                column1="column1", column2="column2", string="5th Approved")


class PurchaseRequestInherit(models.Model):
    _inherit = 'purchase.request'

    is_pr_cash = fields.Boolean(string="Cash PR")
    attachments = fields.Binary(string="Attachments")
    attachments1 = fields.Binary(string="Attachments")
    attachments2 = fields.Binary(string="Attachments")
    attachments3 = fields.Binary(string="Attachments")
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             required=True,
                             copy=False,
                             default='draft')
    assigned_to = fields.Many2one('res.users', 'Approver', required=True)
    department_id = fields.Many2one('category.department', 'Department', required=True)
    date_approved = fields.Date(string="Date Approved")
    dest_location_id = fields.Many2one(comodel_name="stock.location")
    lead_time = fields.Integer(string="Lead Time In Days", compute='compute_lead_time')
    representative_ids = fields.Many2many(comodel_name="res.users")
    is_expense = fields.Boolean(default=False, copy=False)
    approval_users = fields.Many2many(comodel_name="res.users", relation="approval_users", column1="approval_users1",
                                      column2="approval_users2", string="Approval Users")
    is_edit_user = fields.Boolean(default=False)
    project_id = fields.Many2one('project.project', 'Project')
    assign_to = fields.Many2one('res.users', 'Assign To')
    approve_base_approver = fields.Boolean(compute="_compute_approve_base_approver")
    approve_1st_approver_ids = fields.Many2many(related="department_id.approve_1st_approver_ids")
    is_approve_1st_approver = fields.Boolean(compute="check_is_approve_1st_approver")
    approve_2st_approver_ids = fields.Many2many(related="department_id.approve_2st_approver_ids")
    is_approve_2st_approver = fields.Boolean(compute="check_is_approve_2st_approver")
    approve_3st_approver_ids = fields.Many2many(related="department_id.approve_3st_approver_ids")
    is_approve_3st_approver = fields.Boolean(compute="check_is_approve_3st_approver")
    approve_4st_approver_ids = fields.Many2many(related="department_id.approve_4st_approver_ids")
    is_approve_4st_approver = fields.Boolean(compute="check_is_approve_4st_approver")
    approve_5st_approver_ids = fields.Many2many(related="department_id.approve_5st_approver_ids")
    is_approve_5st_approver = fields.Boolean(compute="check_is_approve_5st_approver")
    stock_picking_type_ids = fields.Many2many(comodel_name="stock.picking.type", relation="stock_picking_type_ids",
                                              column1="column1", column2="column2")

    @api.depends('name')
    def check_is_approve_1st_approver(self):
        for rec in self:
            rec.is_approve_1st_approver = False
            if self.env.user.id in rec.approve_1st_approver_ids.ids:
                rec.is_approve_1st_approver = True

    @api.depends('name')
    def check_is_approve_2st_approver(self):
        for rec in self:
            rec.is_approve_2st_approver = False
            if self.env.user.id in rec.approve_2st_approver_ids.ids:
                rec.is_approve_2st_approver = True

    @api.depends('name')
    def check_is_approve_3st_approver(self):
        for rec in self:
            rec.is_approve_3st_approver = False
            if self.env.user.id in rec.approve_3st_approver_ids.ids:
                rec.is_approve_3st_approver = True

    @api.depends('name')
    def check_is_approve_4st_approver(self):
        for rec in self:
            rec.is_approve_4st_approver = False
            if self.env.user.id in rec.approve_4st_approver_ids.ids:
                rec.is_approve_4st_approver = True

    @api.depends('name')
    def check_is_approve_5st_approver(self):
        for rec in self:
            rec.is_approve_5st_approver = False
            if self.env.user.id in rec.approve_5st_approver_ids.ids:
                rec.is_approve_5st_approver = True

    def cancel_purchase_request(self):
        for rec in self:
            rec.state = 'cancel'

    def _compute_approve_base_approver(self):
        _logger.info("Approver base")
        self.approve_base_approver = self.approve_base_approver
        if self.assigned_to.id != False:
            if self.assigned_to.id == self.env.user.id:
                self.approve_base_approver = True

    def send_notify(self, users):
        thread_pool = self.env['mail.thread']
        partner_ids = users.partner_id.ids
        if len(partner_ids) > 0:
            thread_pool.sudo().message_notify(
                partner_ids=partner_ids,
                subject=str('Purchase Request Waiting your Approval'),
                body='Purchase Request Waiting your Approval' + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                    self.id) + '&view_type=form&model=purchase.request&action=" style="font-weight: bold">' + str(
                    self.name) + '</a>',
                email_from=self.env.user.company_id.email,
            )

    def button_base_approver(self):
        self.send_notify(self.approve_1st_approver_ids)
        self.state = "base_approved"

    def button_1st_approver(self):
        self.send_notify(self.approve_2st_approver_ids)
        self.state = "1st_approved"

    def button_2st_approver(self):
        self.send_notify(self.approve_3st_approver_ids)
        self.state = "2st_approved"

    def button_3st_approver(self):
        self.send_notify(self.approve_4st_approver_ids)
        self.state = "3st_approved"

    def button_4st_approver(self):
        self.send_notify(self.approve_5st_approver_ids)
        self.state = "4st_approved"

    def to_approve_approver_back(self):
        self.state = "to_approve"

    def button_base_approver_back(self):
        self.send_notify(self.approve_1st_approver_ids)
        self.state = "base_approved"

    def button_1st_approver_back(self):
        self.send_notify(self.approve_2st_approver_ids)
        self.state = "1st_approved"

    def button_2st_approver_back(self):
        self.send_notify(self.approve_3st_approver_ids)
        self.state = "2st_approved"

    def button_3st_approver_back(self):
        self.send_notify(self.approve_4st_approver_ids)
        self.state = "3st_approved"

    def button_4st_approver_back(self):
        self.send_notify(self.approve_5st_approver_ids)
        self.state = "4st_approved"

    @api.onchange('project_id', 'line_ids')
    def _onchange_project_id(self):
        for rec in self:
            if rec.project_id.id:
                for line in rec.line_ids:
                    line.analytic_account_id = rec.project_id.analytic_account_id.id

    @api.onchange('is_expense')
    def _onchange_is_expense(self):
        for rec in self:
            picking_type = self.env['stock.picking.type'].search([
                ('is_expense', '=', True)
            ]).ids
            if rec.is_expense:
                warehouse = self.env['stock.warehouse'].search([('name', '=', 'General Project')],
                                                                         limit=1).id
                rec.picking_type_id = self.env['stock.picking.type'].search([('warehouse_id', '=', warehouse)],
                                                                         limit=1).id or self.env.ref(
                    'stock.picking_type_in').id
                rec.stock_picking_type_ids = picking_type
            elif not rec.is_expense:
                rec.stock_picking_type_ids = False

    @api.depends('date_approved', 'create_date')
    def compute_lead_time(self):
        for rec in self:
            if rec.date_approved:
                date_format = '%Y-%m-%d'
                date_approved = datetime.strptime(str(rec.date_approved), date_format)
                create_date = datetime.strptime(str(rec.create_date.date()), date_format)
                delta = date_approved - create_date
                rec.lead_time = delta.days

    def button_approved(self):
        res = super(PurchaseRequestInherit, self).button_approved()
        self.date_approved = fields.Date.context_today(self)
        return res


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    def _compute_purchased_qty(self):
        for rec in self:
            rec.purchased_qty = 0.0
            for line in rec.purchase_lines.filtered(
                    lambda x: x.state != 'cancel'):
                if rec.product_uom_id and \
                        line.product_uom != rec.product_uom_id:
                    rec.purchased_qty += line.product_uom._compute_quantity(
                        line.product_qty, rec.product_uom_id)
                else:
                    rec.purchased_qty += line.product_qty

    @api.depends('purchase_lines.state', 'purchase_lines.order_id.state')
    def _compute_purchase_state(self):
        for rec in self:
            temp_purchase_state = False
            if rec.purchase_lines:
                if any([po_line.state == 'done' for po_line in
                        rec.purchase_lines]):
                    temp_purchase_state = 'done'
                elif all([po_line.state == 'cancel' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'cancel'
                elif any([po_line.state == 'purchase' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'purchase'
                elif any([po_line.state == 'to approve' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'to approve'
                elif any([po_line.state == 'sent' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'sent'
                elif all([po_line.state in ('draft', 'cancel') for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'draft'
            rec.purchase_state = temp_purchase_state

    is_pr_cash = fields.Boolean()
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    dest_location_id = fields.Many2one(comodel_name="stock.location",
                                       related='request_id.picking_type_id.default_location_dest_id')
    pr_state = fields.Selection(string="State", related='request_id.state')
    date_approved = fields.Date(string="Date Approved", related='request_id.date_approved')
    lead_time = fields.Integer(string="Lead Time In Days", compute="compute_lead_time")
    representative_ids = fields.Many2many(comodel_name="res.users",
                                          # compute='compute_rep',
                                          store=True)
    po_re_ids = fields.One2many('purchase.order', 'po_request_id', string="Purchase Request")
    purchase_order_id = fields.Many2one(comodel_name="purchase.order", related="purchase_lines.order_id")
    purchase_order_ids = fields.Many2many(comodel_name="purchase.order", relation="purchase_order_ids",
                                          column1="column1",
                                          column2="column2", compute="get_po")

    sub_qty = fields.Float(compute='_compute_dif_qty')
    purchased_qty = fields.Float(string='Quantity in RFQ or PO',
                                 compute="_compute_purchased_qty")
    purchase_state = fields.Selection(
        compute="_compute_purchase_state",
        string="Purchase Status",
        selection=lambda self:
        self.env['purchase.order']._fields['state'].selection,
        store=True,
    )

    @api.depends('purchase_lines')
    def get_po(self):
        for rec in self:
            rec.purchase_order_ids = [(4, po.order_id.id) for po in rec.purchase_lines]

    @api.depends('date_approved', 'create_date')
    def compute_lead_time(self):
        for rec in self:
            rec.lead_time = rec.lead_time
            if rec.date_approved:
                date_format = '%Y-%m-%d'
                date_approved = datetime.strptime(str(rec.date_approved), date_format)
                create_date = datetime.strptime(str(rec.create_date.date()), date_format)
                delta = date_approved - create_date
                rec.lead_time = delta.days

    @api.depends('product_qty', 'purchased_qty')
    def _compute_dif_qty(self):
        for rec in self:
            rec.sub_qty = rec.product_qty - rec.purchased_qty

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if not rec.request_id.department_id:
                raise ValidationError('Must Select Department !')
            else:
                return {
                    'domain': {
                        'product_id': [('categ_id', 'in', rec.request_id.department_id.product_category_ids.ids)]}
                }


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    po_request_id = fields.Many2one(comodel_name="purchase.request.line")
    project_id = fields.Many2one(comodel_name="project.project", string="Project", tracking=True)

    def button_confirm(self):
        res = super(PurchaseOrderInherit, self).button_confirm()
        for rec in self:
            for line in rec.order_line:
                line.product_id.last_purchase_price = line.price_unit
        return res


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_expense = fields.Boolean(default=False, copy=False)


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    @api.model
    def _check_valid_request_line(self, request_line_ids):
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._check_valid_request_line(request_line_ids)

        for line in self.env['purchase.request.line'].browse(request_line_ids):

            if line.sub_qty < 0:
                raise ValidationError(
                    _('Purchase Request %s is Exceed') %
                    line.request_id.name)
        return res


class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    last_purchase_price = fields.Float(string="LPP")
    difference = fields.Float(string="Difference")
    pm = fields.Float(string="PM")

    @api.onchange('price_unit', 'product_id')
    def get_difference(self):
        for rec in self:
            rec.last_purchase_price = rec.product_id.last_purchase_price
            rec.difference = rec.price_unit - rec.last_purchase_price


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    last_purchase_price = fields.Float(string="LPP")
    part_number = fields.Char(string="Part Number")


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    last_purchase_price = fields.Float(string="LPP")
    part_number = fields.Char(string="Part Number")


class ProductCategoryInherit(models.Model):
    _inherit = 'product.category'

    category_department_ids = fields.Many2many(comodel_name="category.department",
                                               relation="category_department_relation",
                                               column1="column2", column2="column1")
    assigned_id_approver = fields.Many2many('res.users', string='Approver', relation="assigned_id_approver",
                                            column1="assigned_id_approver1", column2="assigned_id_approver2",
                                            compute="get_all_users", store=False)
    manager_id = fields.Many2many('res.users', string='Manager', relation="manager_id",
                                  column1="manager_id1", column2="manager_id2", compute="get_all_users", store=False)

    @api.depends('category_department_ids')
    def get_all_users(self):
        for rec in self:
            users = self.env['res.users']
            users |= rec.category_department_ids.approve_1st_approver_ids
            users |= rec.category_department_ids.approve_2st_approver_ids
            users |= rec.category_department_ids.approve_3st_approver_ids
            users |= rec.category_department_ids.approve_4st_approver_ids
            users |= rec.category_department_ids.approve_5st_approver_ids
            rec.assigned_id_approver = users.ids
            rec.manager_id = users.ids
