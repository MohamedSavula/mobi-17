# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError, UserError
from math import copysign


class AssetModifyInherit(models.TransientModel):
    _inherit = 'asset.modify'

    account_id = fields.Many2one(comodel_name="account.account")
    sell_amount = fields.Monetary()

    def sell_dispose(self):
        self.ensure_one()
        if self.gain_account_id == self.asset_id.account_depreciation_id or self.loss_account_id == self.asset_id.account_depreciation_id:
            raise UserError(_("You cannot select the same account as the Depreciation Account"))
        # old code
        # invoice_lines = self.env['account.move.line'] if self.modify_action == 'dispose' else self.invoice_line_ids
        # new code
        invoice_lines = self.env['account.move.line'] if self.modify_action == 'dispose' else {
            'account': self.account_id, 'amount': -self.sell_amount}
        ##############
        return self.asset_id.set_to_close(invoice_line_ids=invoice_lines, date=self.date, message=self.name)


class AccountAssetAssetInherit(models.Model):
    _inherit = 'account.asset'

    code = fields.Char(string='Reference', readonly=True)
    asset_remaining_value = fields.Monetary(string='Depreciable Value', compute='compute_asset_remaining_value',
                                            store=True)
    asset_depreciated_value = fields.Monetary(string='Cumulative Depreciation',
                                              compute='compute_asset_depreciated_value',
                                              store=True)

    @api.depends('depreciation_move_ids', 'depreciation_move_ids.depreciation_value', 'depreciation_move_ids.state',
                 'book_value', 'original_value')
    def compute_asset_remaining_value(self):
        for rec in self:
            rec.asset_remaining_value = rec.book_value

    @api.depends('depreciation_move_ids', 'depreciation_move_ids.depreciation_value',
                 'depreciation_move_ids.state')
    def compute_asset_depreciated_value(self):
        for rec in self:
            rec.asset_depreciated_value = sum(
                rec.depreciation_move_ids.filtered(lambda l: l.state == 'posted').mapped(
                    'depreciation_value'))

    def change_code(self):
        for m in self:
            g = self.search([('parent_id', '=', m.parent_id.id), ('code', '!=', False)])
            if len(g) > 0:
                y = []
                for t in g:
                    y.append(int(t.code))
                m.code = max(y) + 1
            else:
                m.code = int(m.parent_id.code) + 1

    @api.constrains('code')
    def constrains_code(self):
        codes = self.search([('parent_id', '=', self.parent_id.id)])
        if self.code in codes.mapped('id'):
            raise ValidationError("Reference must be unique")

    @api.model
    def create(self, vals):
        asset = super().create(vals)
        if asset.code and 'BILL' in asset.code:
            asset.code = False
        if asset.code == False:
            asset.change_code()
        return asset

    def _get_disposal_moves(self, invoice_lines_list, disposal_date):
        """Create the move for the disposal of an asset.

        :param invoice_lines_list: list of recordset of `account.move.line`
            Each element of the list corresponds to one record of `self`
            These lines are used to generate the disposal move
        :param disposal_date: the date of the disposal
        """

        def get_line(asset, amount, account):
            return (0, 0, {
                'name': asset.name,
                'account_id': account.id,
                'balance': -amount,
                'analytic_distribution': analytic_distribution,
                'currency_id': asset.currency_id.id,
                'amount_currency': -asset.company_id.currency_id._convert(
                    from_amount=amount,
                    to_currency=asset.currency_id,
                    company=asset.company_id,
                    date=disposal_date,
                )
            })

        move_ids = []
        assert len(self) == len(invoice_lines_list)
        for asset, invoice_line_ids in zip(self, invoice_lines_list):
            asset._create_move_before_date(disposal_date)

            analytic_distribution = asset.analytic_distribution

            dict_invoice = {}
            invoice_amount = 0

            initial_amount = asset.original_value
            initial_account = asset.original_move_line_ids.account_id if len(
                asset.original_move_line_ids.account_id) == 1 else asset.account_asset_id

            all_lines_before_disposal = asset.depreciation_move_ids.filtered(lambda x: x.date <= disposal_date)
            depreciated_amount = asset.currency_id.round(copysign(
                sum(all_lines_before_disposal.mapped('depreciation_value')) + asset.already_depreciated_amount_import,
                -initial_amount,
            ))
            # old code
            # for invoice_line in invoice_line_ids:
            #     dict_invoice[invoice_line.account_id] = copysign(invoice_line.balance, -initial_amount) + dict_invoice.get(invoice_line.account_id, 0)
            #     invoice_amount += copysign(invoice_line.balance, -initial_amount)
            # new code
            depreciation_account = asset.account_depreciation_id
            dict_invoice[invoice_line_ids.get('account', False)] = copysign(invoice_line_ids.get('amount', 0),
                                                                            -initial_amount) + dict_invoice.get(
                invoice_line_ids.get('account', False), 0)
            ########
            invoice_amount += copysign(invoice_line_ids.get('amount', 0), -initial_amount)

            list_accounts = [(amount, account) for account, amount in dict_invoice.items()]
            difference = -initial_amount - depreciated_amount - invoice_amount
            difference_account = asset.company_id.gain_account_id if difference > 0 else asset.company_id.loss_account_id
            line_datas = [(initial_amount, initial_account),
                          (depreciated_amount, depreciation_account)] + list_accounts + [
                             (difference, difference_account)]
            vals = {
                'asset_id': asset.id,
                'ref': asset.name + ': ' + (_('Disposal') if not invoice_line_ids else _('Sale')),
                'asset_depreciation_beginning_date': disposal_date,
                'date': disposal_date,
                'journal_id': asset.journal_id.id,
                'move_type': 'entry',
                'line_ids': [get_line(asset, amount, account) for amount, account in line_datas if account],
            }
            asset.write({'depreciation_move_ids': [(0, 0, vals)]})
            move_ids += self.env['account.move'].search([('asset_id', '=', asset.id), ('state', '=', 'draft')]).ids

        return move_ids

