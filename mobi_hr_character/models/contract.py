# -*- coding: utf-8 -*-
from odoo import models, fields


class ContractLeaves(models.Model):
    _name = 'contract.leaves'

    name = fields.Char(required=True)


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    employee_category_id = fields.Many2one(comodel_name="employee.category")
    leaves_id = fields.Many2one(comodel_name="contract.leaves")
    # leaves Details
    auto_leaves_allocated = fields.Boolean(copy=False)
    # Contract details
    end_of_trail_period = fields.Date()
    number_working_days_month = fields.Integer()
    number_working_hours_day = fields.Integer()
    number_of_salary_multipliers = fields.Float(string="Number Of Salary Multipliers for Short Term")
    total_loan_short_term_budget = fields.Float()
    number_of_salary_long_term = fields.Float(string="Number Of Salary Multipliers for Long Term")
    total_loan_long_term_budget = fields.Float()
