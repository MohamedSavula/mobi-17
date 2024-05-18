# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # page allowance
    eg_mobile_allowance = fields.Float()
    labour_allowance = fields.Float()
    meal_allowance = fields.Float()
    sales_transportation_allowance = fields.Float()
    transportation_allowance = fields.Float()
    one_percentage_allowance = fields.Float(string="1 %")
    transportation_benefits_allowance = fields.Float()
    pay_insurance_deduction = fields.Float()
    medical_deduction = fields.Float()
    accident_deduction = fields.Float()
    car_allowance = fields.Float()
    living_subsidy_allowance = fields.Float()
    # salary information
    is_insured = fields.Boolean(string="Is Insured?", default=True)
    fixed_insurance = fields.Float(string="Insurance Amount")
    variable_insurance = fields.Float(string="Variable Insurance Amount")
    average_variables_of_previous_year = fields.Float()
    is_employer = fields.Boolean("Is Employer")
    bank_wage = fields.Monetary()
    cash_wage = fields.Monetary()
    basic_salary = fields.Monetary()
    fixed_other_allowance = fields.Monetary()
    fixed_transportation_allowance = fields.Monetary()
    natural_allowance = fields.Monetary(string="Nature Allowance")
    previous_special_bonus = fields.Monetary()
    special_bonus = fields.Monetary()
    medical_upgrade = fields.Float()

    @api.onchange('basic_salary', 'fixed_other_allowance', 'fixed_transportation_allowance', 'natural_allowance',
                  'previous_special_bonus')
    def get_wage_sum(self):
        for rec in self:
            rec.wage = (rec.basic_salary + rec.fixed_other_allowance + rec.fixed_transportation_allowance +
                        rec.natural_allowance + rec.previous_special_bonus)

    @api.onchange('basic_salary', 'fixed_other_allowance', 'fixed_transportation_allowance', 'natural_allowance',
                  'previous_special_bonus', 'special_bonus', 'labour_allowance')
    def get_fixed_insurance_sum(self):
        for rec in self:
            rec.fixed_insurance = (rec.basic_salary + rec.fixed_other_allowance + rec.fixed_transportation_allowance +
                                   rec.natural_allowance + rec.previous_special_bonus +
                                   rec.special_bonus + rec.labour_allowance)

    @api.onchange('wage', 'cash_wage')
    def get_bank_wage(self):
        for rec in self:
            rec.bank_wage = rec.wage - rec.cash_wage
