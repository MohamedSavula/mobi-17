# -*- coding: utf-8 -*-
from odoo import fields, models, api


class CentionePurchaseRequest(models.Model):
    _name = "centione.purchase.request"
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(readonly=True)
    purchase_lines_ids = fields.One2many('centione.purchase.request.line', 'request_id')
    delivery_request_id = fields.Many2one(comodel_name="centione.delivery.request", string="Delivery Request")
    initial_order_id = fields.Integer()
    state = fields.Selection([
        ('open', 'Open'),
        ('approved', 'Approved by Manager'),
        ('done', 'Done')
    ], default='open', index=True, readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    origin = fields.Char(string="Source Document")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('centione.purchase.request')
        return super(CentionePurchaseRequest, self).create(vals)

    def approve_manager(self):
        return self.write({'state': 'approved'})

    def done_request(self):
        return self.write({'state': 'done'})


class CentionePurchaseRequestLine(models.Model):
    _name = "centione.purchase.request.line"
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def default_picking_type(self):
        picking_type = int(
            self.env['ir.config_parameter'].sudo().get_param('picking_type_first_id', default=0)) or False
        return picking_type

    product_id = fields.Many2one('product.product', required=True)
    qty = fields.Float()
    cost_price = fields.Float(string="Cost Price")
    delivery_request_line_id = fields.Integer()
    initial_mrp_line_id = fields.Integer()
    uom_id = fields.Many2one('product.uom')
    request_id = fields.Many2one('centione.purchase.request')
    picking_type_id = fields.Many2one('stock.picking.type', default=default_picking_type)
    type = fields.Selection([('sister', 'Sister Company'), ('normal', 'Normal Purchase Request')])
    notes = fields.Text()
    purchase_order_ids = fields.Many2many('purchase.order')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved by Manager'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], default='draft', readonly=True)
    planned_date = fields.Date("Schedule Date")

    def cancel_line(self):
        self.ensure_one()
        all_lines = self.search([('state', '=', 'draft'), ('request_id', '=', self.request_id.id)])
        if not all_lines:
            self.request_id.state = 'done'
        return self.write({'state': 'cancel'})

    def manager_approve(self):
        return self.write({'state': 'approved'})

    @api.onchange('product_id')
    def onchange_product(self):
        self.update({'cost_price': self.product_id.standard_price})
