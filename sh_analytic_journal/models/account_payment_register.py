# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    analytic_account_tag = fields.Boolean(
        string="Analytic Account & Tags"
    )

    analytic_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account"
    )

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string="Analytic Tags"
    )