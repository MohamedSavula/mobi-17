# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    total_unpaid_loan = fields.Float(string="Total Loan Unpaid", compute='_compute_total_loan_unpaid', required=False, )

    def rule_long_term(self, payslip):
        if payslip.loan_lines_ids:
            loan_amount = 0

            loan_amount = sum((one_loan_line.amount - one_loan_line.paid_amount) for one_loan_line in
                              payslip.loan_lines_ids.filtered(lambda line: line.loan_type == 'long_term'))
            return loan_amount
        else:
            return 0

    def rule_short_term(self, payslip):
        if payslip.loan_lines_ids:
            loan_amount = 0

            loan_amount = sum((one_loan_line.amount - one_loan_line.paid_amount) for one_loan_line in
                              payslip.loan_lines_ids.filtered(lambda line: line.loan_type == 'short_term'))
            return loan_amount
        else:
            return 0

    def Get_Loan_Rule(self, payslip):
        loan_amount = 0
        if payslip.loan_lines_ids:
            loan_amount = sum(
                (one_loan_line.amount - one_loan_line.paid_amount) for one_loan_line in payslip.loan_lines_ids)
        return loan_amount

    def _compute_total_loan_unpaid(self):
        for rec in self:
            total_unpaid_loan = 0
            loan_line_obj = self.env['hr.loan.line']
            if rec.id:
                loan_line_data = loan_line_obj.search(
                    [('loan_id.employee_id', '=', rec.id), ('state', 'in', ('unpaid', 'partial_paid'))])
                for loan_line in loan_line_data:
                    total_unpaid_loan += loan_line.amount - loan_line.paid_amount

            rec.total_unpaid_loan = total_unpaid_loan
            return True
