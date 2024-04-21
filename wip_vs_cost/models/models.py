# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountWipCostInherit(models.Model):
    _name = "account.wip.cost"

    account_id_wip = fields.Many2one("account.account", string="wip")
    account_id_cost = fields.Many2one("account.account", string="cost")


class AssetDepreciationConfirmationWizard(models.Model):
    _name = "generate.be.invoice.wizard"

    start_date = fields.Date(string="Start", required=True)
    end_date = fields.Date(string="End", required=True)

    def convert_str_to_int(self, l):
        return [int(x) for x in l]

    def generate_be_invoice_project(self):
        for rec in self:
            domain = [('account_id.account_type', '=', 'income'), ('credit', '!=', False),
                      ('analytic_distribution', '!=', False), ('date', '>=', rec.start_date),
                      ('date', '<=', rec.end_date), ('parent_state', '=', 'posted')]
            liens = self.env['account.move.line'].sudo().search(domain)
            new_liens = self.env['account.move.line']
            new_analytics = self.env['account.analytic.account']
            for line in liens:
                ids_list = rec.convert_str_to_int(line.analytic_distribution.keys())
                analytics = self.env['account.analytic.account'].sudo().browse(ids_list)
                if any(analytic.state in ['draft', 'in_progres'] for analytic in analytics):
                    new_liens |= line
            if new_liens:
                for line in new_liens:
                    ids_list = rec.convert_str_to_int(line.analytic_distribution.keys())
                    analytics = self.env['account.analytic.account'].sudo().browse(ids_list)
                    new_analytics |= analytics.filtered(lambda a: a.state in ['draft', 'in_progres'])
                new_analytics.update({'state': 'invoiced'})
                for analytic in new_analytics:
                    domain = [('account_id.is_wib', '=', True), ('debit', '!=', False),
                              ('analytic_distribution', '=', {str(analytic.id): 100}), ('date', '>=', rec.start_date),
                              ('date', '<=', rec.end_date), ('parent_state', '=', 'posted')]
                    liens = self.env['account.move.line'].sudo().search(domain)
                    if liens:
                        jet = self.env['account.move'].sudo().create({
                            'ref': analytic.name,
                            'move_type': 'entry',
                        })
                        for lien in liens:
                            cost_account_id = self.env['account.wip.cost'].sudo().search(
                                [('account_id_wip', '=', lien.account_id.id)], limit=1).account_id_cost
                            if cost_account_id and lien.debit:
                                jet.line_ids = [
                                    (0, 0, {'debit': 0, 'credit': lien.debit, 'account_id': lien.account_id.id,
                                            'analytic_distribution': {analytic.id: 100},
                                            'analytic_tag_ids': analytic.analytic_tag_ids.ids}),
                                    (0, 0, {'debit': lien.debit, 'credit': 0, 'account_id': cost_account_id.id,
                                            'analytic_distribution': {analytic.id: 100},
                                            'analytic_tag_ids': analytic.analytic_tag_ids.ids})]
                        if jet.line_ids:
                            jet.action_post()
                        else:
                            jet.unlink()
