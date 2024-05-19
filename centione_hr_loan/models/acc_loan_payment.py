# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class LoanPayment(models.Model):
    _name = 'loan.payment'

    name = fields.Char()
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    partner_type = fields.Selection(
        [('customer', 'Customer'),
         ('vendor', 'Vendor'),
         ('none', 'None'),
         ('both', 'Customer and Vendor')], string='Partner Type')
    req_amount = fields.Float(string='Requested Amount')
    desc = fields.Char(string='Loan')
    req_date = fields.Date(string='Date Of Request')
    state = fields.Selection(
        [('open', 'Open'),
         ('closed', 'Done'),
         ], default='open', string='State')
    loan_installment_date = fields.Date()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('loan.payment')
        return super(LoanPayment, self).create(vals)

