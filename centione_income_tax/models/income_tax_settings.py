# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class IncomeTaxSettings(models.Model):
    _name = 'income.tax.settings'

    name = fields.Char(string="Name", required=False, )
    line_ids = fields.One2many(comodel_name="income.tax.settings.line", inverse_name="income_tax_id",
                               string="Taxes Divisions", required=False, ondelete='cascade')
    is_functional_exempt = fields.Boolean(string="Function Exemption", )
    functional_exempt_value = fields.Float(string="Functional Exemption Value", required=False, digits=(12, 6))

    @api.constrains('line_ids')
    def check_line_ids(self):
        if self.line_ids:
            prev = self.line_ids[0].max_value
            for line in self.line_ids[1:]:
                if abs(prev - line.min_value) > 0.0001:
                    raise ValidationError('Tax Division Is Missing')
                prev = line.max_value

    def calc_income_tax(self, tax_pool, employee):
        income_tax_settings = self.env.ref('centione_income_tax.income_tax_settings0')
        emp = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('employee_id.is_a_handicap', '=', True)])
        if emp:
            functional_exemption = income_tax_settings.is_functional_exempt and income_tax_settings.functional_exempt_handicap_value or 0
        else:
            functional_exemption = income_tax_settings.is_functional_exempt and income_tax_settings.functional_exempt_value or 0
        effective_salary = tax_pool - functional_exemption
        income_tax = 0
        income_tax_after_exemption = 0

        starting_beginning_segment_sequence = 1
        for line in income_tax_settings.line_ids:
            if line.min_value <= effective_salary <= line.max_value:
                starting_beginning_segment_sequence = line.beginning_segment_sequence
                break

        entered_first_segment = False
        for line in income_tax_settings.line_ids:
            if line.diff_value:
                if line.sequence >= starting_beginning_segment_sequence:
                    if not entered_first_segment:
                        entered_first_segment = True
                        effective_salary -= line.max_value
                        income_tax += (line.tax_ratio / 100.0) * line.max_value

                    elif 0 < effective_salary <= line.diff_value:
                        income_tax += (line.tax_ratio / 100.0) * effective_salary
                        income_tax_after_exemption = (100 - line.discount_ratio) / 100.0 * income_tax
                        break

                    elif effective_salary > line.diff_value:
                        effective_salary -= line.diff_value
                        income_tax += (line.tax_ratio / 100.0) * line.diff_value
            else:
                income_tax += (line.tax_ratio / 100.0) * effective_salary
                break
        return income_tax_after_exemption

    def calc_next_tax(self, tax_pool, employee, payslip):
        previous_tax = 0
        previous_tax_pool = 0
        salary_slips = self.env['hr.payslip'].search([
            ('state', '=', 'done'),
            ('date_to', '<=', payslip.date_to),
            ('date_from', '>=', payslip.date_from),
            ('employee_id', '=', employee.id)], order='date_to desc')
        salary_slips_filtered = salary_slips.filtered(
            lambda x: 'INCTAX' in x.line_ids.mapped('code') or 'NXTTAX' in x.line_ids.mapped('code'))
        for salary_slip in salary_slips_filtered:
            for line in salary_slip.line_ids:
                if line.code in ['INCTAX', 'NXTTAX']:
                    previous_tax += abs(line.total)
                    break
                elif line.category_id.code in ['BASIC', 'ALW', 'DED']:
                    previous_tax_pool += line.total

        tax_amount = self.calc_income_tax(tax_pool + previous_tax_pool) - previous_tax
        return tax_amount


class IncomeTaxSettingsLine(models.Model):
    _name = 'income.tax.settings.line'
    _order = 'min_value asc'

    income_tax_id = fields.Many2one(comodel_name="income.tax.settings", string="Income Tax Settings", required=False, )
    max_value = fields.Float(string="Maximum Value", required=False, digits=(12, 6))
    diff_value = fields.Float(string="Difference Value", required=False, compute='compute_diff_value', digits=(12, 6))
    tax_ratio = fields.Float(string="Tax Ratio %", required=False, digits=(12, 6))
    discount_ratio = fields.Float(string="Discount Ratio %", required=False, digits=(12, 6))

    sequence = fields.Integer(string="Sequence", required=False)
    min_value = fields.Float(string="Minimum Value", required=False, digits=(12, 6))

    beginning_segment_sequence = fields.Integer(default=1)

    @api.depends('max_value', 'max_value')
    def compute_diff_value(self):
        for rec in self:
            if rec.max_value:
                rec.diff_value = rec.max_value - rec.min_value

    @api.constrains('max_value', 'max_value', 'discount_ratio', 'tax_ratio')
    def check_all_values(self):
        if self.max_value and self.min_value and self.max_value < self.min_value:
            raise ValidationError('Minimum Value Can not be greater than maximum value')
        if self.tax_ratio < 0 or self.tax_ratio > 100:
            raise ValidationError('Tax Ratio Must Be Between 0 and 100')
        if self.discount_ratio < 0 or self.discount_ratio > 100:
            raise ValidationError('Discount Ratio Must Be Between 0 and 100')
