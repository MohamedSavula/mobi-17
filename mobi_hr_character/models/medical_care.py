# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrMedicalCare(models.Model):
    _name = 'hr.medical.care'

    medical_status = fields.Selection(string="Medical Status",
                                      selection=[('yes', 'Yes'), ('no', 'No')],
                                      required=False,
                                      default='yes')
    medical_id = fields.Char(string='Medical ID')
    medical_grade = fields.Char(string='Medical Grade')
    insurance_company = fields.Char(string='Insurance Company')
    employee_id = fields.Many2one("hr.employee")
    spouse = fields.Char()
    spouse_birth_date = fields.Date()
    spouse_insured = fields.Boolean()
    child_ids = fields.Many2many('hr.employee.child', domain="[('employee_id', '=', employee_id)]")
    value = fields.Float()
    tax_fees = fields.Float()
    total = fields.Float(compute='_compute_total', store=True)
    per_month = fields.Float()
    share_type = fields.Selection([('value', 'Value'), ('percentage', 'Percentage')], default='percentage')
    employee_share = fields.Float()
    company_share = fields.Float()
    total_share = fields.Float(compute='_compute_total_share')

    @api.depends('employee_share', 'company_share')
    def _compute_total_share(self):
        self.total_share = self.employee_share + self.company_share

    @api.depends('value', 'tax_fees')
    def _compute_total(self):
        self.total = self.tax_fees + self.value
