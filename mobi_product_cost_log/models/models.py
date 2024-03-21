# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields
from odoo.addons import decimal_precision as dp


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    cost_change_ids = fields.One2many(comodel_name='cost.change', inverse_name='cost_product_id')

    def write(self, values):
        res = super(ProductProductInherit, self).write(values)
        if 'standard_price' in values:
            self.cost_change_ids = [(0, 0, {
                'cost_product_id': self.id,
                'cost_value': values['standard_price'],
                'change_date': fields.Datetime.now()
            })]
        return res


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    cost_change_ids = fields.One2many(comodel_name='cost.change', inverse_name='cost_product_id')


class CostChange(models.Model):
    _name = 'cost.change'
    _rec_name = 'cost_product_id'

    cost_product_id = fields.Many2one(comodel_name="product.product")
    cost_value = fields.Float(digits=dp.get_precision('Product Price'))
    standard_price = fields.Float('Cost', related='cost_product_id.standard_price')
    change_date = fields.Datetime()
