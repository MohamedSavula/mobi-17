# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil import rrule


class HrLeaveInherit(models.Model):
    _inherit = 'hr.leave'

    @api.onchange('date_from', 'date_to', 'employee_id', 'request_unit_half', 'holiday_status_id')
    def _onchange_leave_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.holiday_status_id.consume_weekends and rec.request_date_to and rec.request_date_from:
                diff = (rec.date_to.date() - rec.date_from.date()).total_seconds() / 86400.0
                if rec.request_unit_half:
                    rec.number_of_days = .5
                else:
                    rec.number_of_days = diff + 1 if diff >= 0 else 0
                if rec.holiday_status_id.public_holiday:
                    if rec.number_of_days > 0:
                        for m in self.env['hr.holidays.public.line'].search([(1, '=', 1)]):
                            if m.date and rec.request_date_to >= m.date >= rec.request_date_from:
                                rec.number_of_days -= 1
                    if rec.number_of_days < 0:
                        rec.number_of_days = 0
            elif rec.date_from and rec.date_to and rec.request_date_to and rec.request_date_from and rec.employee_id:
                resource_calendar = rec.employee_id.resource_calendar_id
                _weekdays = list({int(d) for d in resource_calendar.attendance_ids.mapped('dayofweek')})
                if _weekdays:
                    weekdays = _weekdays
                else:
                    raise ValidationError(_('No valid Work Schedule found.'))

                date_from = rec.request_date_from
                date_to = rec.request_date_to

                # An iterable that represents the days an employee has to attend from date_from to date_to
                # based on work schedule
                scheduled_workdays = rrule.rrule(rrule.DAILY, dtstart=date_from, wkst=rrule.SU,
                                                 until=date_to, byweekday=weekdays)
                dates = []
                for day in scheduled_workdays:
                    dates.append(day)
                if rec.request_unit_half:
                    rec.number_of_days = .5
                else:
                    days, hours = rec._get_duration()
                    rec.number_of_hours = hours
                    rec.number_of_days = days
                if rec.holiday_status_id.public_holiday:
                    if rec.number_of_days > 0:
                        for m in rec.env['hr.holidays.public.line'].search([(1, '=', 1)]):
                            if m.date and rec.request_date_to >= m.date >= rec.request_date_from:
                                if m.date in dates:
                                    rec.number_of_days -= 1
                    if rec.number_of_days < 0:
                        rec.number_of_days = 0
            else:
                rec.number_of_days = 0


class HrLeaveTypeInherit(models.Model):
    _inherit = 'hr.leave.type'

    is_legal_leaves = fields.Boolean(copy=False)
    is_unpaid = fields.Boolean(copy=False)
    consume_weekends = fields.Boolean(copy=False)
    is_carried_over = fields.Boolean(copy=False)
    public_holiday = fields.Boolean(copy=False)
    end_service_incentive = fields.Boolean(copy=False)
    apply_double_validation = fields.Boolean(copy=False)
    transfer_from = fields.Boolean(copy=False)
    transfer_to = fields.Boolean(copy=False)
    open_carried_over = fields.Boolean(copy=False)
