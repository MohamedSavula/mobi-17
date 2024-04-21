# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class HrExcuse(models.Model):
    _name = 'hr.excuse'
    _rec_name = 'name'
    _description = 'hr_excuse'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.excuse')
        return super(HrExcuse, self).create(vals)

    def unlink(self):
        for record in self:
            list = ['approved', 'refused']
            if record.state in list:
                raise ValidationError(_('You Can Not Delete The Excuse in State ' + record.state))
            else:
                return super(HrExcuse, self).unlink()

    def _needaction_domain_get(self):
        employee_id = False
        if self.env.user.id:
            employee_obj = self.env['hr.employee']
            employee_data = employee_obj.search([('user_id', '=', self.env.user.id)], limit=1, )
            if (employee_data):
                employee_id = employee_data[0].id

        if employee_id:
            return [('state', 'in', ['new']), ('employee_id', '!=', employee_id)]
        else:
            return []

    def _employee_get(self):
        hr_employee_obj = self.env['hr.employee']
        employee_data = hr_employee_obj.search([('user_id', '=', self.env.user.id)], limit=1, )
        if employee_data:
            return employee_data[0]

    def _get_date_now(self):
        res = datetime.now().date()
        return res

    def get_contract(self, employee, date_from, date_to):
        """
        @param employee: recordset of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
        """
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), '|', '|'] + clause_1 + clause_2 + clause_3
        return self.env['hr.contract'].search(clause_final).ids

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_contract_id(self):
        for rec in self:
            date_from = rec.date_from
            date_to = rec.date_to
            employee = rec.employee_id
            contract_id = False
            if date_from and date_to and employee:
                contract = rec.get_contract(employee, date_from, date_to)
                if contract:
                    contract_id = contract[0]

            rec.contract_id = contract_id

    def action_draft(self):
        for rec in self:
            if rec.resource_calendar_leaves_id:
                rec.resource_calendar_leaves_id.unlink()

            rec.state = 'draft'

    def action_approved(self):
        for rec in self:
            rec._check_contract_id()
            if rec.employee_id and rec.contract_id:
                if not rec.contract_id.resource_calendar_id:
                    raise ValidationError(_('Not Working Schedule	In Contract'))
            rec.state = 'approved'

    def action_refused(self):
        for rec in self:
            rec.state = 'refused'

    def action_send_to_manager(self):
        for rec in self:
            rec._check_contract_id()
            rec.state = 'manager_approved'

    def action_manager_approved(self):
        for rec in self:
            rec._check_contract_id()
            rec.state = 'manager_approved'

    @api.constrains('date_from', 'date_to')
    def validate_excuse_mission_time(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_from > rec.date_to:
                    raise ValidationError(_('The To Date Must be The Largest Than From Date.'))

    @api.depends('date_from', 'date_to')
    def _get_period(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_from < rec.date_to:
                    date_from_datetime = datetime.strptime(str(rec.date_from), "%Y-%m-%d %H:%M:%S")
                    date_to_datetime = datetime.strptime(str(rec.date_to), "%Y-%m-%d %H:%M:%S")
                    number_of_days = (date_to_datetime - date_from_datetime)
                    if number_of_days.days > 1:
                        raise ValidationError(_('Period Must not exceed one day'))
                    else:
                        rec.period = number_of_days

    def from_delta_to_hours(self, self_diff):
        total_hours = 0
        if self_diff:
            days, hours, minutes = self_diff.days, self_diff.seconds // 3600, self_diff.seconds // 60 % 60
            total_hours = (days * 24) + (hours) + (minutes / 60)
        return total_hours

    @api.constrains('contract_id')
    def _check_contract_id(self):
        for rec in self:
            contract_id = rec.contract_id
            if not contract_id:
                raise ValidationError(_('This Employee Not Have Contract In This Period.'))
                return False
            else:
                number_excuse_month = rec.employee_id.number_excuse_month
                period_excuse_month = rec.employee_id.period_excuse_month
                period_one_excuse = rec.employee_id.period_one_excuse

                date_from_datetime = datetime.strptime(str(rec.date_from), "%Y-%m-%d %H:%M:%S")
                date_to_datetime = datetime.strptime(str(rec.date_to), "%Y-%m-%d %H:%M:%S")
                self_diff = date_to_datetime - date_from_datetime
                diff_one = rec.from_delta_to_hours(self_diff)
                if diff_one > period_one_excuse:
                    raise ValidationError(
                        _('The Period Of This Request Is Larger Than Configuration Hours : %s') % str(period_one_excuse))

                month = date_from_datetime.strftime('%Y-%m')
                day_from = date_from_datetime.strftime('%Y-%m-%d')
                excuse_day_from_data = self.search([('employee_id', '=', rec.employee_id.id), ('day_from', '=', day_from)],
                                                   order='date_from Desc')
                if len(excuse_day_from_data) > 1:
                    raise ValidationError(_('This Employee Have Excuse In This Day : %s') % (day_from))

                excuse_data = self.search(
                    [('employee_id', '=', rec.employee_id.id), ('month', '=', month), ('state', '=', 'approved')],
                    order='date_from Desc')
                count = 0
                hours = 0
                if (excuse_data):
                    for one_excuse in excuse_data:
                        count += 1

                        d_from = one_excuse.date_from
                        df_dt = datetime.strptime(str(one_excuse.date_from), "%Y-%m-%d %H:%M:%S")
                        dt_dt = datetime.strptime(str(one_excuse.date_to), "%Y-%m-%d %H:%M:%S")
                        diff = dt_dt - df_dt

                        one_hours = rec.from_delta_to_hours(diff)
                        hours += one_hours

                if count >= number_excuse_month:
                    raise ValidationError(
                        _('The Number Of Requests Month Is Larger Than Configuration Total Numbers : %s') % str(
                            number_excuse_month))

                if hours >= period_excuse_month:
                    raise ValidationError(
                        _('The Period Of This Month Is Larger Than Configuration Hours : %s') % str(period_excuse_month))

    @api.depends('date_from')
    def _compute_month(self):
        for rec in self:
            if rec.date_from:
                date_from_datetime = datetime.strptime(str(rec.date_from), "%Y-%m-%d %H:%M:%S")
                month = date_from_datetime.strftime('%Y-%m')
                rec.month = month

    @api.depends('date_from')
    def _compute_day_from(self):
        for rec in self:
            if rec.date_from:
                date_from_datetime = datetime.strptime(str(rec.date_from), "%Y-%m-%d %H:%M:%S")
                day_from = date_from_datetime.strftime('%Y-%m-%d')
                rec.day_from = day_from

    name = fields.Char('Serial', track_visibility='onchange', )
    employee_id = fields.Many2one(comodel_name="hr.employee", track_visibility='onchange', string="Employee",
                                  default=_employee_get, required=True, )
    contract_id = fields.Many2one(comodel_name="hr.contract", track_visibility='onchange', string="Contract",
                                  compute=_compute_contract_id, store=True, required=False, )
    resource_calendar_leaves_id = fields.Many2one(comodel_name="resource.calendar.leaves", track_visibility='onchange',
                                                  string="Leaves", required=False, )
    date = fields.Date(string="Date", default=_get_date_now, track_visibility='onchange', required=False, )
    date_from = fields.Datetime(string="From Date", track_visibility='onchange', required=True, )
    date_to = fields.Datetime(string="To Date", track_visibility='onchange', required=True, )

    day_from = fields.Char(string="Day", compute=_compute_day_from, store=True, required=False, )

    month = fields.Char(string="Month", compute=_compute_month, store=True, required=False, )
    reason = fields.Text(string="Reason", required=True, track_visibility='onchange', )
    period = fields.Char(string="Period", track_visibility='onchange', required=False, compute=_get_period, store=True)
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'),
                                        ('manager_approved', 'Manager Approved'), ('approved', 'Approved'),
                                        ('refused', 'Refused')],
                             required=False, readonly=True, track_visibility='onchange', default='draft')
