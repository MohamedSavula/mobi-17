# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import date


class HrSuspended(models.Model):
    _name = 'hr.suspended'
    _rec_name = 'name'
    _description = 'Termination'
    _order = 'name asc, id desc'

    name = fields.Char(string="Name", related='employee_id.name')

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department")
    job_id = fields.Many2one(comodel_name="hr.job", string="Job Title")
    responsible_id = fields.Many2one(comodel_name="hr.employee", string="Responsible")
    state = fields.Selection(string="State",
                             selection=[('cancel', 'Cancel'), ('draft', 'Draft'), ('approved', 'Approved'), ],
                             default='draft')
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    approve_date = fields.Date(string="Approve Date")
    reason = fields.Text(string="Reason")

    def check_suspension(self):
        suspensions = self.env['hr.suspended'].search([('state', '=', 'approved')])
        for suspension in suspensions:
            if suspension.date_to < date.today():
                if suspension.employee_id and suspension.employee_id.state == 'suspended':
                    suspension.employee_id.state = 'active'

    @api.onchange('employee_id')
    def onchange_employee(self):
        for rec in self:
            rec.update({'department_id': rec.employee_id.department_id.id, 'job_id': rec.employee_id.job_id.id})

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_approved(self):
        for rec in self:
            rec.write({'state': 'approved', 'approve_date': fields.Date.today()})
