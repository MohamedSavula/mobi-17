# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging

LOGGER = logging.getLogger(__name__)


class ProductsCatWizard(models.TransientModel):
    _name = 'products.category.wizard'

    def _get_domain(self):
        ids = []
        delivery_request_id = self.env.context.get('active_id')
        delivery_request = self.env['centione.delivery.request'].browse(delivery_request_id)
        for line in delivery_request.delivery_lines_ids:
            if line.is_manager and not line.is_approved2:
                ids.append(line.id)
        return [('id', 'in', ids)]

    delivery_request_line_ids = fields.Many2many(comodel_name="centione.delivery.request.line",
                                                 string="Delivery Request Lines", domain=_get_domain)

    def approve_lines(self):
        for rec in self.delivery_request_line_ids:
            rec.approve_line()
