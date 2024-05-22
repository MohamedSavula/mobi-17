# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    is_petty_cash = fields.Boolean()


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    is_advance = fields.Boolean()
    is_petty_cash = fields.Boolean()

    def create(self, vals_list):
        res = super(AccountPaymentInherit, self).create(vals_list)
        if type(vals_list) == type({}):
            destination_account_id = vals_list.get('destination_account_id', False)
            res = super(AccountPaymentInherit, self).create(vals_list)
            res.destination_account_id = destination_account_id
            return res
        return res

    @api.depends('partner_id', 'journal_id', 'destination_journal_id')
    def _compute_is_internal_transfer(self):
        # for payment in self:
        pass
        # payment.is_internal_transfer = payment.partner_id and payment.partner_id == payment.journal_id.company_id.partner_id and payment.destination_journal_id

    @api.onchange('is_petty_cash')
    def get_journal_petty_cash(self):
        for rec in self:
            if rec.is_petty_cash:
                rec.destination_journal_id = self.env['account.journal'].sudo().search([('is_petty_cash', '=', True)],
                                                                                       limit=1).id

    @api.onchange('is_advance', 'partner_id', 'currency_id')
    def get_account_from_partner(self):
        for rec in self:
            if rec.is_advance and rec.partner_id:
                account_id = rec.partner_id.contact_line_ids.filtered(
                    lambda l: l.account_id.currency_id == rec.currency_id and l.is_approved)
                if account_id:
                    rec.destination_account_id = account_id[0].account_id.id
            if not rec.is_advance and rec.partner_id:
                if rec.partner_type == 'customer' and rec.currency_id.id != rec.partner_id.property_account_receivable_id.currency_id.id or rec.partner_type == 'supplier' and rec.currency_id.id != rec.partner_id.property_account_payable_id.currency_id.id:
                    account_id = rec.partner_id.contact_line_ids.filtered(
                        lambda l: l.account_id.currency_id == rec.currency_id and not l.is_approved)
                    if account_id:
                        rec.destination_account_id = account_id[0].account_id.id
