# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountLoanJournalInherit(models.Model):
    _inherit = "account.journal"

    is_loan_journal = fields.Boolean(string='Is Loan?')

    @api.constrains('is_loan_journal')
    def check_another_loan(self):
        obj = self.env['account.journal'].search([('is_loan_journal', '=', True)])
        if len(obj) > 1:
            raise ValidationError(_('There is Another Journal is Loan'))
