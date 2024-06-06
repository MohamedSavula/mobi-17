# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    entry_accrued_id = fields.Many2one(comodel_name="account.move")

    def action_post(self):
        res = super(AccountMoveInherit, self).action_post()
        for rec in self:
            if rec.is_accrued:
                account_accrued = self.env['account.account'].search([('is_accrued', '=', True)], limit=1)
                account_revenue = self.env['account.account'].search([('actual_revenue', '=', True)], limit=1)
                if not account_accrued or not account_revenue:
                    raise UserError(
                        "You must create an accrued account and an actual revenue account in the configuration.")
                balance = sum(self.env['account.move.line'].search(
                    [('partner_id', '=', rec.partner_id.id), ('account_id', '=', account_accrued.id)]).mapped(
                    'balance'))
                rec.entry_accrued_id = self.env['account.move'].create({
                    'move_type': 'entry',
                    'date': fields.Date.today(),
                    'ref': rec.name,
                    'line_ids': [
                        (0, 0, {
                            'name': rec.name,
                            'partner_id': rec.partner_id.id,
                            'account_id': account_accrued.id,
                            'balance': -balance,
                        }),
                        (0, 0, {
                            'name': rec.name,
                            'partner_id': rec.partner_id.id,
                            'account_id': account_revenue.id,
                            'balance': balance,
                        }),
                    ],
                }).id
        return res
