# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging
from datetime import date

LOGGER = logging.getLogger(__name__)


class HrSuspended(models.Model):
    _name = 'hr.suspended'
    _rec_name = 'name'
    _description = 'Termination'
    _order = 'name asc, id desc'

    def check_suspension(self):
        suspensions = self.env['hr.suspended'].search([('state', '=', 'approved')])
        for suspension in suspensions:
            if suspension.date_to < date.today():
                if suspension.employee_id and suspension.employee_id.state == 'suspended':
                    suspension.employee_id.state = 'active'

    name = fields.Char(string="Name", related='employee_id.name', required=False, )

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, )
    department_id = fields.Many2one(comodel_name="hr.department", string="Department")
    job_id = fields.Many2one(comodel_name="hr.job", string="Job Title")
    responsible_id = fields.Many2one(comodel_name="hr.employee", string="Responsible", required=False, )
    state = fields.Selection(string="State",
                             selection=[('cancel', 'Cancel'), ('draft', 'Draft'), ('approved', 'Approved'), ],
                             default='draft', required=False, )
    date_from = fields.Date(string="Date From", required=False, )
    date_to = fields.Date(string="Date To", required=False, )
    approve_date = fields.Date(string="Approve Date", required=False, )
    reason = fields.Text(string="Reason", required=False, )

    @api.onchange('employee_id')
    def onchange_employee(self):
        for rec in self:
            rec.update({'department_id': rec.employee_id.department_id.id, 'job_id': rec.employee_id.job_id.id})

    def action_cancel(self):
        for rec in self:
            return rec.write({'state': 'cancel'})

    def action_approved(self):
        for rec in self:
            rec.employee_id.state = 'suspended'
            return rec.write({'state': 'approved', 'approve_date': fields.Date.today()})
