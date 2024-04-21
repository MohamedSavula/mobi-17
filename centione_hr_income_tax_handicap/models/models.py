# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HREmployeeInh(models.Model):
    _inherit = 'hr.employee'

    is_a_handicap = fields.Boolean(
        string='Is a Handicap')


class IncomeTaxSettingInh(models.Model):
    _inherit = 'income.tax.settings'

    functional_exempt_handicap_value = fields.Float(
        string='Functional exemption Handicap value')
