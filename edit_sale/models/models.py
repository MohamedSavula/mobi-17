# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    attention = fields.Text(string="Attention")
    is_fire_stock = fields.Boolean(string="", )
    project_id = fields.Many2one(comodel_name="project.project")
    reference_type = fields.Selection(string="", selection=[('vendor_po', 'Vendor Po'), ('loi', 'LOI'),
                                                            ('contract', 'Contract')])
    reference = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()


class SaleOrderLineInh(models.Model):
    _inherit = "sale.order.line"

    penetrant_size_diameter = fields.Char(string="Penetrant Size (MM) Diameter", required=False, )
    side = fields.Char()
    solution = fields.Char(string="Solution", required=False, )
    is_fire_stock = fields.Boolean(string="", related="order_id.is_fire_stock")
