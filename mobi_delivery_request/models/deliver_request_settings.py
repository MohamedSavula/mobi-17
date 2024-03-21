# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging

LOGGER = logging.getLogger(__name__)


class DeliveryRequestSettings(models.TransientModel):
    _name = 'delivery.request.settings'

    picking_type_first_id = fields.Many2one(comodel_name="stock.picking.type", string="First Picking Type")
    picking_type_second_id = fields.Many2one(comodel_name="stock.picking.type", string="Second Picking Type")
    picking_type_purchase_id = fields.Many2one(comodel_name="stock.picking.type", string="Purchase Picking Type")

    @api.model
    def default_get(self, fields):
        res = super(DeliveryRequestSettings, self).default_get(fields)
        params = self.env['ir.config_parameter'].sudo()
        picking_type_first_id = int(params.get_param('picking_type_first_id', default=0)) or False
        picking_type_second_id = int(params.get_param('picking_type_second_id', default=0)) or False
        picking_type_purchase_id = int(params.get_param('picking_type_purchase_id', default=0)) or False
        res.update(
            picking_type_first_id=picking_type_first_id, picking_type_second_id=picking_type_second_id
            , picking_type_purchase_id=picking_type_purchase_id
        )
        return res

    def execute(self):
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('picking_type_first_id', (self.picking_type_first_id.id or False), )
        params.set_param('picking_type_second_id', (self.picking_type_second_id.id or False), )
        params.set_param('picking_type_purchase_id', (self.picking_type_purchase_id.id or False), )
