# -*- coding: utf-8 -*-
from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.depends('wage', 'number_of_salary_multipliers')
    def compute_total_loan_budget(self):
        for rec in self:
            total_loan_budget = 0
            if rec.wage and rec.number_of_salary_multipliers:
                total_loan_budget = rec.wage * rec.number_of_salary_multipliers
            rec.total_loan_budget = total_loan_budget
            return True

    @api.depends('wage', 'number_of_salary_multipliers_long')
    def compute_total_loan_budget_long(self):
        for rec in self:
            total_loan_budget_long = 0
            if rec.wage and rec.number_of_salary_multipliers_long:
                total_loan_budget_long = rec.wage * rec.number_of_salary_multipliers_long
            rec.total_long_term_loan_budget = total_loan_budget_long
            return True

    number_of_salary_multipliers = fields.Float(string="Number Of Salary Multipliers for Short Term",
                                                default=1.2,
                                                required=False, )
    number_of_salary_multipliers_long = fields.Float(string="Number Of Salary Multipliers for Long Term",
                                                     default=1.2,
                                                     required=False, )
    total_loan_budget = fields.Float(string="Total Loan short Term Budget",
                                     compute=compute_total_loan_budget,
                                     store=True,
                                     required=False, )
    total_long_term_loan_budget = fields.Float(string="Total Loan long Term Budget",
                                               compute=compute_total_loan_budget_long,
                                               store=True,
                                               required=False, )
