# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    loan_lines_ids = fields.One2many(comodel_name="hr.loan.line",
                                     inverse_name="payslip_id", compute='_get_loan_lines',
                                     store=True, string="Loan Lines", required=False, )

    def action_payslip_done(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')
        obj = super(HrPayslip, self).action_payslip_done()
        for slip in self:
            if slip and slip.loan_lines_ids:

                total_loans = []
                loan_id = False
                for line in slip.loan_lines_ids:
                    line.write({'state': 'paid'})
                    line.update({'paid_amount': line.amount})
                    line.accounting_register(installment=line.amount)
                    if line.loan_id not in total_loans:
                        total_loans.append(line.loan_id)

                if total_loans:
                    for loan_id in total_loans:
                        all_loans_lines = self.env['hr.loan.line'].search(
                            [('loan_id', '=', loan_id.id), ('loan_id.state', '=', 'approved')])
                        open = False
                        for line_loan in all_loans_lines:
                            if line_loan.state != 'paid':
                                open = True

                        if not open:
                            loan_id.write({'state': 'closed'})

        return obj

    def Get_Loan_Rule(self, payslip):
        loan_amount = 0
        if payslip.loan_lines_ids:
            loan_amount = sum(
                (one_loan_line.amount - one_loan_line.paid_amount) for one_loan_line in payslip.loan_lines_ids)
        return loan_amount

    @api.depends('employee_id', 'date_from', 'date_to')
    def _get_loan_lines(self):
        for rec in self:
            line_ids = []
            if rec.employee_id and rec.date_from and rec.date_to:
                loans_lines = self.env['hr.loan.line'].search(
                    [('loan_id.employee_id', '=', self.employee_id.id), ('loan_id.state', 'in', ['sent','approved']),
                     ('state', 'in', ('unpaid', 'partial_paid')),
                     ('date', '>=', rec.date_from),
                     ('date', '<=', rec.date_to)])
                for line in loans_lines:
                    line_ids.append(line.id)
                    # line.write({'payslip_id': self.id})

                rec.loan_lines_ids = line_ids
                return

            return True

    def compute_sheet(self):
        for rec in self:
            rec._get_loan_lines()
        res = super(HrPayslip, self).compute_sheet()
        return res


