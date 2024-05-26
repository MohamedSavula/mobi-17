# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    payment_reconcile_id = fields.Many2many(comodel_name="account.payment", copy=False)
    select = fields.Boolean(copy=False)
    amount_reconcile = fields.Float(compute="get_amount_reconcile", readonly=False, store=True)
    residual_amount_reconcile = fields.Float(compute="get_residual_amount_reconcile", store=True, readonly=False)
    is_tax = fields.Boolean()

    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = False
            move.invoice_has_outstanding = False

            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue

            pay_term_lines = move.line_ids \
                .filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))

            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('parent_state', '=', 'posted'),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]

            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

            if move.is_inbound():
                domain.append(('balance', '<', 0.0))
                payments_widget_vals['title'] = _('Outstanding credits')
            else:
                domain.append(('balance', '>', 0.0))
                payments_widget_vals['title'] = _('Outstanding debits')

            for line in self.env['account.move.line'].search(domain):

                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = line.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )

                if move.currency_id.is_zero(amount):
                    continue

                payments_widget_vals['content'].append({
                    'journal_name': line.move_id.name,
                    'amount': amount,
                    'currency_id': move.currency_id.id,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'date': fields.Date.to_string(line.date),
                    'account_payment_id': line.payment_id.id,
                })

            if not payments_widget_vals['content']:
                continue

            move.invoice_outstanding_credits_debits_widget = payments_widget_vals
            move.invoice_has_outstanding = True

    @api.constrains('ref')
    def check_ref_uniqe(self):
        for rec in self:
            ref = self.search([('ref', '!=', False), ('ref', '=', rec.ref), ('id', '!=', rec.id),
                               ('partner_id', '=', rec.partner_id.id)])
            if ref and rec.move_type in ('out_invoice', 'in_invoice'):
                raise UserError(_("Bill Reference already exists"))

    @api.depends('amount_residual')
    def get_amount_reconcile(self):
        for rec in self:
            rec.amount_reconcile = rec.amount_residual

    @api.depends('amount_residual', 'amount_reconcile')
    def get_residual_amount_reconcile(self):
        for rec in self:
            rec.residual_amount_reconcile = rec.amount_residual - rec.amount_reconcile

    @api.onchange('amount_reconcile')
    def check_amount_reconcile(self):
        for rec in self:
            if rec.amount_reconcile + rec.residual_amount_reconcile > rec.amount_residual:
                raise UserError(_("You can not reconcile invoice %s" % rec.name))


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    def open_invoice_reconcile(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'context': {'name_payment': self.name},
            'domain': [('payment_reconcile_id', 'in', self.ids)]
        }

    def action_open_manual_reconciliation_widget(self):
        ''' Open the manual reconciliation widget for the current payment.
        :return: A dictionary representing an action.
        '''
        self.ensure_one()
        if not self.is_advance:
            if not self.partner_id:
                raise UserError(_("Payments without a customer can't be matched"))

            liquidity_lines, counterpart_lines, writeoff_lines = self._seek_for_lines()

            action_context = {'company_ids': self.company_id.ids, 'partner_ids': self.partner_id.ids}
            if self.partner_type == 'customer':
                action_context.update({'mode': 'customers'})
            elif self.partner_type == 'supplier':
                action_context.update({'mode': 'suppliers'})

            if counterpart_lines:
                action_context.update({'move_line_id': counterpart_lines[0].id})

            return {
                'type': 'ir.actions.client',
                'tag': 'manual_reconciliation_view',
                'context': action_context,
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Reconcile Payment',
                'res_model': 'select.invoice.reconcile',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_payment_id': self.id,
                    'default_invoices_ids': self.env['account.move'].sudo().search(
                        [('move_type', '=', 'in_invoice' if self.partner_type == 'supplier' else 'out_invoice'),
                         ('partner_id', '=', self.partner_id.id), ('amount_residual', '!=', 0),
                         ('state', '=', 'posted'),
                         ('payment_state', 'not in', ('paid', 'in_payment'))]).ids,
                },
            }


class SelectInvoiceReconcile(models.Model):
    _name = 'select.invoice.reconcile'
    _description = 'SelectInvoiceReconcile'

    @api.model
    def get_account_tax_id(self):
        account = self.env['account.account'].sudo().search([('code', '=', '201000002')], limit=1)
        return account.id

    @api.model
    def get_journal_tax_id(self):
        journal = self.env['account.journal'].sudo().search([('code', '=', 'TA')], limit=1)
        return journal.id

    payment_id = fields.Many2one(comodel_name="account.payment")
    invoices_ids = fields.Many2many(comodel_name="account.move")
    partials_amount = fields.Float(compute="get_partials_amount")
    account_tax_id = fields.Many2one(comodel_name="account.account", default=get_account_tax_id)
    journal_tax_id = fields.Many2one(comodel_name="account.journal", default=get_journal_tax_id)

    @api.onchange('payment_id')
    def get_partials_amount(self):
        for rec in self:
            partials_amount = rec.payment_id.line_ids.filtered(
                lambda l: l.account_id == rec.payment_id.destination_account_id).amount_residual_currency
            rec.partials_amount = partials_amount if partials_amount > 0 else -partials_amount

    def reconcile(self):
        for rec in self:
            invoices = rec.invoices_ids.filtered(lambda i: i.select)
            invoices.update({
                "select": False
            })
            invoices.check_amount_reconcile()
            total_liens = sum(invoices.mapped('amount_reconcile'))
            if total_liens > rec.partials_amount:
                raise UserError(_("Total reconcile must be %s" % rec.partials_amount))
            payment_line = rec.payment_id.line_ids.filtered(
                lambda l: l.account_id == rec.payment_id.destination_account_id)
            for invoice in invoices:
                invoice_line = invoice.line_ids.filtered(lambda l: l.account_id == invoice.account_id)
                (payment_line | invoice_line).create_journal_entry_reconcile(invoice.amount_reconcile,
                                                                             invoice.residual_amount_reconcile,
                                                                             rec.account_tax_id, rec.journal_tax_id)


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    def create_journal_entry_reconcile(self, amount_reconcile=False, residual_amount_reconcile=False,
                                       account_tax_id=False, journal_tax_id=False):
        destination_account_id = False
        account_id = False
        amount = []
        new_entry = self.env['account.move']
        payment_id = False
        invoice_id = False
        invoice_line = False
        payment_line = False
        for rec in self:
            if rec.move_id.move_type == 'entry':
                payment_id = rec.payment_id
                amount.append(rec.debit)
                destination_account_id = rec.payment_id.destination_account_id
                payment_line = rec
            if rec.move_id.move_type != 'entry':
                invoice_id = rec.move_id
                amount.append(rec.credit)
                account_id = rec.move_id.account_id
                invoice_line = rec
        if destination_account_id and account_id:
            new_entry = self.env['account.move'].sudo().create({
                'move_type': 'entry',
                'ref': payment_id.name + '/' + invoice_id.name,
                'line_ids': [(0, 0, {
                    'account_id': destination_account_id.id,
                    'partner_id': payment_line.partner_id.id,
                    'currency_id': payment_line.currency_id.id,
                    'amount_currency': -(
                            amount_reconcile or min(amount)) if payment_id.partner_type == 'supplier' else (
                            amount_reconcile or min(amount)),
                }), (0, 0, {
                    'account_id': account_id.id,
                    'partner_id': payment_line.partner_id.id,
                    'currency_id': payment_line.currency_id.id,
                    'amount_currency': (
                            amount_reconcile or min(amount)) if payment_id.partner_type == 'supplier' else -(
                            amount_reconcile or min(amount)),
                }), ],
            })
            new_entry.payment_id = False
            new_entry.action_post()
            new_entry.payment_id = payment_id.id
        move_lines = self | new_entry.line_ids
        move_lines.filtered(lambda l: l.account_id == destination_account_id).with_context(
            reduced_line_sorting=True).reconcile()
        move_lines.filtered(lambda l: l.account_id == account_id).with_context(reduced_line_sorting=True).reconcile()
        invoice_id.payment_reconcile_id = [(4, payment_id.id)]
        if invoice_line.move_id.is_tax and residual_amount_reconcile > 0:
            if not journal_tax_id or not account_tax_id:
                raise UserError(_("Please add account tax and journal tax"))
            new_entry_tax = self.env['account.move'].sudo().create({
                'move_type': 'entry',
                'journal_id': journal_tax_id.id,
                'ref': payment_id.name + '/aaa' + invoice_id.name,
                'line_ids': [(0, 0, {
                    'account_id': invoice_line.account_id.id,
                    'partner_id': invoice_line.move_id.partner_id.id,
                    'currency_id': payment_line.currency_id.id,
                    'amount_currency': -residual_amount_reconcile if invoice_line.debit else residual_amount_reconcile,
                }), (0, 0, {
                    'account_id': account_tax_id.id,
                    'partner_id': payment_line.partner_id.id,
                    'currency_id': payment_line.currency_id.id,
                    'amount_currency': residual_amount_reconcile if invoice_line.debit else -residual_amount_reconcile,
                }), ],
            })
            new_entry_tax.payment_id = False
            new_entry_tax.action_post()
            new_entry_tax.payment_id = payment_id.id
            (invoice_line | new_entry_tax.line_ids.filtered(
                lambda l: l.account_id == invoice_line.account_id)).with_context(reduced_line_sorting=True).reconcile()
            invoice_line.move_id.invoice_line_ids = [(0, 0, {
                'name': "Withholding",
                'price_withholding': -residual_amount_reconcile,
                'account_id': 258,
                'tax_ids': False,
            })]