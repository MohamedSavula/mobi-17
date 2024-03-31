# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields, api


class AccountAnalyticTag(models.Model):
    _name = 'account.analytic.tag'
    _description = 'Account Analytic Tag'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")


class AccountAnalyticAccountInherit(models.Model):
    _inherit = 'account.analytic.account'

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string="Analytic Tags"
    )


class AccountAnalyticPlanInherit(models.Model):
    _inherit = 'account.analytic.plan'

    code = fields.Char(string="Code")


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string="Analytic Tags"
    )

    @api.onchange('analytic_distribution')
    def get_analytic_tag(self):
        for rec in self:
            if rec.analytic_distribution:
                accounts = [int(x) for x in rec.analytic_distribution.keys()]
                accounts_ids = self.env['account.analytic.account'].browse(accounts)
                rec.analytic_tag_ids = accounts_ids.analytic_tag_ids.ids
            else:
                rec.analytic_tag_ids = False


class AccountPayment(models.Model):
    _inherit = 'account.payment'

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

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountPayment, self).create(vals_list)
        if res.move_id and res.move_id.line_ids and res.analytic_id:
            for line in res.move_id.line_ids:
                line.sudo().write({
                    "analytic_distribution": {res.analytic_id.id: 100},
                    'analytic_tag_ids': [(6, 0, res.analytic_tag_ids.ids)]
                })
        return res

    def write(self, vals):
        res = super(AccountPayment, self).write(vals)
        if self and self.move_id and self.move_id.line_ids and self.analytic_id:
            for line in self.move_id.line_ids:
                line.sudo().write({
                    "analytic_distribution": {self.analytic_id.id: 100},
                    'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]
                })
        return res
