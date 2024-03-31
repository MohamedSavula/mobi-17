# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"

    is_wib = fields.Boolean(copy=False, related="account_id.is_wib")
    is_accrued = fields.Boolean(copy=False, related="account_id.is_accrued")
    actual_revenue = fields.Boolean(copy=False, related="account_id.actual_revenue")
    is_actual = fields.Boolean(copy=False, related="account_id.is_actual")


class AccountAccountInherit(models.Model):
    _inherit = 'account.account'

    is_wib = fields.Boolean(copy=False)
    is_accrued = fields.Boolean(copy=False)
    actual_revenue = fields.Boolean(copy=False)
    is_actual = fields.Boolean(copy=False)
    is_withholding = fields.Boolean(copy=False)
    is_vat = fields.Boolean(copy=False)


class AnalyticAccountInherit(models.Model):
    _inherit = 'account.analytic.account'

    wib_balance = fields.Float(compute="_get_cost_accounts")
    actual_cost = fields.Float(compute="_get_cost_accounts")
    accrued_cost = fields.Float(compute="_get_cost_accounts")
    actual_revenue = fields.Float(compute="_get_cost_accounts")

    def _get_cost_accounts(self):
        for rec in self:
            rec.wib_balance = 0
            rec.actual_cost = 0
            rec.accrued_cost = 0
            rec.actual_revenue = 0
            if rec.state in ['draft', 'in_progres']:
                wib_balance = self.env['account.move.line'].search(
                    [("analytic_distribution", "=", {rec.id: 100}), ('is_wib', '=', True),
                     ('parent_state', '=', 'posted')])
                rec.wib_balance = sum(wib_balance.mapped('debit')) - sum(wib_balance.mapped('credit'))
            if rec.state == 'invoiced':
                actual_cost = self.env['account.move.line'].search(
                    [("analytic_distribution", "=", {rec.id: 100}), ('is_actual', '=', True),
                     ('parent_state', '=', 'posted')])
                rec.actual_cost = sum(actual_cost.mapped('debit')) - sum(actual_cost.mapped('credit'))
            accrued_cost = self.env['account.move.line'].search(
                    [("analytic_distribution", "=", {rec.id: 100}), ('is_accrued', '=', True),
                     ('parent_state', '=', 'posted')])
            rec.accrued_cost = sum(accrued_cost.mapped('debit')) - sum(accrued_cost.mapped('credit'))
            actual_revenue = self.env['account.move.line'].search(
                [("analytic_distribution", "=", {rec.id: 100}), ('actual_revenue', '=', True),
                 ('parent_state', '=', 'posted')])
            rec.actual_revenue = sum(actual_revenue.mapped('credit')) - sum(actual_revenue.mapped('debit'))
