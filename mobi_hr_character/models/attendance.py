# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AttendanceManualAbsence(models.Model):
    _name = 'attendance.manual.absence'
    _description = 'Attendance Manual Absence'

    employee_id = fields.Many2one('hr.employee')
    date_from = fields.Date()
    date_to = fields.Date()
    payslip_date = fields.Date()


class AttendanceAbsence(models.Model):
    _name = 'attendance.absence'
    _description = 'Attendance Absence'

    name = fields.Char(compute='_compute_name')
    employee_id = fields.Many2one('hr.employee')
    date = fields.Date()
    payslip_date = fields.Date()

    @api.depends('employee_id', 'date')
    def _compute_name(self):
        self.name = "%s for %s" % (self.employee_id.name, str(self.date))
