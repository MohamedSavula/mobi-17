# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string="Analytic Tags"
    )
