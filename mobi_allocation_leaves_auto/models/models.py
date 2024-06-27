# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta


class LeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    checked = fields.Boolean('checked', default=True)


class LeaveType(models.Model):
    _inherit = 'hr.leave.type'

    auto_every_year = fields.Boolean('Auto Every Year')
    depend_on_age = fields.Boolean("Depends On Age And Insurance ")
    number_of_days = fields.Float('Number Of Days')
    number_of_days_more_than_50_year = fields.Float('Number Of Days For > 50')
    number_of_days_less_than_50_year = fields.Float('Number Of Days For < 50')
    six_months_of_hire_date = fields.Boolean('6 Months Of Hire Date')
    start_date = fields.Date()
    end_date = fields.Date()
    # more_than_50_year = fields.Boolean('Exceeded 50 Years')
    # less_than_50_year = fields.Boolean('Not exceeded 50 Years')


class mobi_allocation_leaves_auto(models.Model):
    _inherit = 'hr.employee'

    create_allocation_leaves = fields.Boolean("No Create Allocation leaves")
    old_insurance_years = fields.Integer('Social Insurance Date For Vacation Balance', track_visibility="always")

    def exceeded_50_year_date(self, dates):
        for m in self:
            if m.birthday or m.insurance_start_date:
                if m.birthday and m.insurance_start_date:
                    a_month1 = relativedelta(years=50)
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month2 = relativedelta(years=remain)
                    else:
                        a_month2 = relativedelta(years=0)
                    diff1 = dates - a_month1
                    diff2 = dates - a_month2
                    if diff1 > m.birthday or diff2 > m.insurance_start_date:
                        return True
                    else:
                        return False

                elif m.birthday:
                    a_month1 = relativedelta(years=50)
                    diff1 = dates - a_month1
                    if diff1 > m.birthday:
                        return True
                    else:
                        return False


                elif m.insurance_start_date:
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month1 = relativedelta(years=remain)
                    else:
                        a_month1 = relativedelta(years=0)
                    diff2 = dates - a_month1
                    if diff2 > m.insurance_start_date:
                        return True
                    else:
                        return False

    def get_date_of_exceeded(self):
        for m in self:
            if m.birthday or m.insurance_start_date:
                if m.birthday and m.insurance_start_date:
                    a_month1 = relativedelta(years=50)
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month2 = relativedelta(years=remain)
                    else:
                        a_month2 = relativedelta(years=0)
                    diff1 = m.birthday + a_month1
                    diff2 = m.insurance_start_date + a_month2
                    return min(diff1, diff2)

                elif m.birthday:
                    a_month1 = relativedelta(years=50)
                    diff1 = m.birthday + a_month1
                    return diff1


                elif m.insurance_start_date:
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month1 = relativedelta(years=remain)
                    else:
                        a_month1 = relativedelta(years=0)
                    diff2 = m.insurance_start_date + a_month1
                    return diff2

    def exceeded_50_year(self):
        for m in self:
            if m.birthday or m.insurance_start_date:
                if m.birthday and m.insurance_start_date:
                    a_month1 = relativedelta(years=50)
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month2 = relativedelta(years=remain)
                    else:
                        a_month2 = relativedelta(years=0)
                    diff1 = fields.Date.today() - a_month1
                    diff2 = fields.Date.today() - a_month2
                    if diff1 > m.birthday or diff2 > m.insurance_start_date:
                        return True
                    else:
                        return False

                elif m.birthday:
                    a_month1 = relativedelta(years=50)
                    diff1 = fields.Date.today() - a_month1
                    if diff1 > m.birthday:
                        return True
                    else:
                        return False


                elif m.insurance_start_date:
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month1 = relativedelta(years=remain)
                    else:
                        a_month1 = relativedelta(years=0)
                    diff2 = fields.Date.today() - a_month1
                    if diff2 > m.insurance_start_date:
                        return True
                    else:
                        return False

    def create_allocations(self):
        today = date.today()
        leaves = self.env['hr.leave.type'].search(
            [('auto_every_year', '=', True), ('start_date', '<=', today), ('end_date', '>=', today)])
        employees = self.env['hr.employee'].search([('create_allocation_leaves', '=', False)])
        for leave in leaves:
            if leave.depend_on_age:
                for m in employees:
                    six_months = relativedelta(months=6)
                    diff = fields.Date.today() - six_months
                    if m.first_hire_date:
                        if m.first_hire_date < diff:
                            if m.exceeded_50_year():
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': leave.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'checked': True,
                                    'date_from': datetime(datetime.now().year, 1, 1),
                                    'number_of_days': leave.number_of_days_more_than_50_year,
                                })
                                allocation.action_validate()
                            elif not m.exceeded_50_year():
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': leave.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'checked': False,
                                    'date_from': datetime(datetime.now().year, 1, 1),
                                    'number_of_days': leave.number_of_days_less_than_50_year,
                                })
                                allocation.action_validate()
                    else:
                        if m.exceeded_50_year():
                            allocation = self.env['hr.leave.allocation'].create({
                                'name': leave.name,
                                'holiday_status_id': leave.id,
                                'holiday_type': 'employee',
                                'employee_id': m.id,
                                'checked': True,
                                'date_from': datetime(datetime.now().year, 1, 1),
                                'number_of_days': leave.number_of_days_more_than_50_year,
                            })
                            allocation.action_validate()
                        elif not m.exceeded_50_year():
                            allocation = self.env['hr.leave.allocation'].create({
                                'name': leave.name,
                                'holiday_status_id': leave.id,
                                'holiday_type': 'employee',
                                'employee_id': m.id,
                                'checked': False,
                                'date_from': datetime(datetime.now().year, 1, 1),
                                'number_of_days': leave.number_of_days_less_than_50_year,
                            })
                            allocation.action_validate()

            else:
                for m in employees:
                    six_months = relativedelta(months=6)
                    diff = fields.Date.today() - six_months
                    if m.first_hire_date:
                        if m.first_hire_date < diff:
                            allocation = self.env['hr.leave.allocation'].create({
                                'name': leave.name,
                                'holiday_status_id': leave.id,
                                'holiday_type': 'employee',
                                'employee_id': m.id,
                                'date_from': datetime(datetime.now().year, 1, 1),
                                'number_of_days': leave.number_of_days,
                            })
                            allocation.action_validate()
                    else:
                        allocation = self.env['hr.leave.allocation'].create({
                            'name': leave.name,
                            'holiday_status_id': leave.id,
                            'holiday_type': 'employee',
                            'employee_id': m.id,
                            'date_from': datetime(datetime.now().year, 1, 1),
                            'number_of_days': leave.number_of_days,
                        })
                        allocation.action_validate()

    def create_allocations_hire_date(self):
        today = date.today()
        leaves = self.env['hr.leave.type'].search(
            [('auto_every_year', '=', True), ('start_date', '<=', today), ('end_date', '>=', today)])
        six_months_of_hire_date_leave = self.env['hr.leave.type'].search(
            [('six_months_of_hire_date', '=', True), ('start_date', '<=', today), ('end_date', '>=', today)],
            limit=1)
        employees = self.env['hr.employee'].search([('create_allocation_leaves', '=', False)])
        for leave in leaves:
            if leave.depend_on_age:
                for m in employees:
                    if m.first_hire_date:
                        six_months = relativedelta(months=6)
                        diff = fields.Date.today() - six_months
                        if diff == m.first_hire_date:
                            if m.exceeded_50_year():
                                if m.exceeded_50_year_date(diff):
                                    allocation = self.env['hr.leave.allocation'].create({
                                        'name': leave.name,
                                        'holiday_status_id': six_months_of_hire_date_leave.id,
                                        'holiday_type': 'employee',
                                        'employee_id': m.id,
                                        'checked': True,
                                        'date_from': datetime(datetime.now().year, datetime.now().month,
                                                              datetime.now().day),
                                        'number_of_days': (leave.number_of_days_more_than_50_year / 2)
                                    })
                                    allocation.action_validate()
                                else:
                                    if m.get_date_of_exceeded():
                                        sum1 = leave.number_of_days_more_than_50_year
                                        day_per_month = sum1 / 12
                                        date_difference = relativedelta(date.today(), m.get_date_of_exceeded())
                                        months = date_difference.months + (date_difference.days / 30)
                                        number_of_days = months * day_per_month
                                        sum1 = leave.number_of_days_less_than_50_year
                                        day_per_month = sum1 / 12
                                        date_difference = relativedelta(m.get_date_of_exceeded(), diff)
                                        months = date_difference.months + (date_difference.days / 30)
                                        number_of_days += (months * day_per_month)
                                        allocation = self.env['hr.leave.allocation'].create({
                                            'name': leave.name,
                                            'holiday_status_id': six_months_of_hire_date_leave.id,
                                            'holiday_type': 'employee',
                                            'employee_id': m.id,
                                            'checked': True,
                                            'date_from': datetime(datetime.now().year, datetime.now().month,
                                                                  datetime.now().day),
                                            'number_of_days': number_of_days,
                                        })
                                        allocation.action_validate()
                                sum = leave.number_of_days_more_than_50_year
                                day_per_month = sum / 12
                                date_difference = relativedelta(date(date.today().year, 12, 31), date.today())
                                months = date_difference.months + (date_difference.days / 30)
                                number_of_days = months * day_per_month
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': m.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'date_from': datetime(datetime.now().year, datetime.now().month,
                                                          datetime.now().day),
                                    'number_of_days': number_of_days,
                                    'checked': True,
                                })
                                allocation.action_validate()

                            elif not m.exceeded_50_year():
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': leave.name,
                                    'holiday_status_id': six_months_of_hire_date_leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'date_from': datetime(datetime.now().year, datetime.now().month,
                                                          datetime.now().day),
                                    'number_of_days': leave.number_of_days_less_than_50_year / 2,
                                    'checked': True,
                                })
                                allocation.action_validate()
                                sum = leave.number_of_days_less_than_50_year
                                day_per_month = sum / 12
                                date_difference = relativedelta(date(date.today().year, 12, 31), date.today())
                                months = date_difference.months + (date_difference.days / 30)
                                number_of_days = months * day_per_month
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': m.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'date_from': datetime(datetime.now().year, datetime.now().month,
                                                          datetime.now().day),
                                    'number_of_days': number_of_days,
                                    'checked': False,
                                })
                                allocation.action_validate()
            else:
                for m in employees:
                    if m.first_hire_date:
                        six_months = relativedelta(months=6)
                        diff = fields.Date.today() - six_months
                        if diff == m.first_hire_date:
                            if True:
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': leave.name,
                                    'holiday_status_id': six_months_of_hire_date_leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'date_from': datetime(datetime.now().year, datetime.now().month,
                                                          datetime.now().day),
                                    'number_of_days': leave.number_of_days / 2,
                                    'checked': True,
                                })
                                allocation.action_validate()
                                sum = leave.number_of_days
                                day_per_month = sum / 12
                                date_difference = relativedelta(date(date.today().year, 12, 31), date.today())
                                months = date_difference.months + (date_difference.days / 30)
                                number_of_days = months * day_per_month
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': m.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'date_from': datetime(datetime.now().year, datetime.now().month,
                                                          datetime.now().day),
                                    'number_of_days': number_of_days,
                                    'checked': True,
                                })
                                allocation.action_validate()

    def check_allocations(self):
        # r=relativedelta(date.today(),date(date.today().year,1,1))
        # print(r)
        # r = relativedelta(date(date.today().year,12,31),date.today())
        # print(r)
        allocations = self.env['hr.leave.allocation'].search(
            [('holiday_status_id.depend_on_age', '=', True), ('holiday_status_id.auto_every_year', '=', True),
             ('checked', '=', False)])
        for m in allocations:
            if m.date_from.year == datetime.now().year:
                if m.employee_id.exceeded_50_year():
                    # leaves = self.env['hr.leave.type'].search([('auto_every_year', '=', True),('less_than_50_year','=',True)])
                    sum = 0
                    for leave in m.holiday_status_id:
                        sum += leave.number_of_days_less_than_50_year
                    day_per_month = sum / 12
                    date_difference = relativedelta(date.today(),
                                                    date(m.date_from.year, m.date_from.month, m.date_from.day))
                    months = date_difference.months + (date_difference.days / 30)
                    number_of_days = months * day_per_month
                    m.action_refuse()
                    m.action_draft()
                    m.number_of_days = number_of_days
                    m.checked = True
                    m.action_validate()
                    # leaves = self.env['hr.leave.type'].search(
                    #     [('auto_every_year', '=', True), ('more_than_50_year', '=', True)])
                    sum = 0
                    for leave in m.holiday_status_id:
                        sum += leave.number_of_days_more_than_50_year
                    day_per_month = sum / 12
                    date_difference = relativedelta(date(date.today().year, 12, 31), date.today())
                    months = date_difference.months + (date_difference.days / 30)
                    number_of_days = months * day_per_month
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': m.name,
                        'holiday_status_id': m.holiday_status_id.id,
                        'holiday_type': 'employee',
                        'employee_id': m.employee_id.id,
                        'date_from': datetime.combine(date.today(), datetime.min.time()),
                        'number_of_days': number_of_days,
                        'checked': True,
                    })
                    allocation.action_validate()
