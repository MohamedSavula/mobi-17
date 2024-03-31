# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TermsAndCondition(models.Model):
    _name = 'terms.and.condition'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Terms And Condition'

    name = fields.Char(string="Name", required=True, tracking=True)
    show_in_po = fields.Boolean(tracking=True)


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def get_terms_and_condition(self):
        terms_and_condition = self.env['terms.and.condition'].sudo().search([('show_in_po', '=', True)])
        return terms_and_condition.ids

    terms_and_condition_ids = fields.Many2many(comodel_name="terms.and.condition", string="Terms And Condition",
                                               default=get_terms_and_condition)
