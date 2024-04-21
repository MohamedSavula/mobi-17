# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class mobi_script_leaves(models.Model):
    _inherit='hr.employee'

    reduced_leaves = fields.Float(string='Reduced',force_save=True,default=0)

    def reduce_leaves(self):
        for rec in self:
            date = datetime.date(2020,1,1)
            date_2 = datetime.date(2019,12,31)
            annual_leave=rec.env['hr.leave.type'].search([('name','=','Annual Leave'),('validity_start','=',date)],limit=1)
            result=annual_leave.get_days(rec.id)
            result_days = result.get(annual_leave.id, {})
            if result_days.get('remaining_leaves',0) >15 :
                leaves_to_reduce = result_days.get('remaining_leaves',0) - 15
                allocations = self.env['hr.leave.allocation'].search([
                    ('employee_id', '=', rec.id),
                    ('state', 'in', ['validate']),
                    ('holiday_status_id', 'in', annual_leave.ids)
                ])
                for alloc in allocations:
                    if alloc.date_from.date() == date or alloc.date_from.date() == date_2:
                        alloc.action_refuse()
                        alloc.action_draft()
                        alloc.number_of_days -= leaves_to_reduce
                        alloc.action_confirm()
                        alloc.action_approve()
                        rec.reduced_leaves += leaves_to_reduce
                        break

    def return_leaves(self):
        for rec in self:
            date = datetime.date(2020, 1, 1)
            date_2 = datetime.date(2019, 12, 31)
            annual_leave = rec.env['hr.leave.type'].search(
                [('name', '=', 'Annual Leave'), ('validity_start', '=', date)], limit=1)
            result = annual_leave.get_days(rec.id)
            result_days = result.get(annual_leave.id, {})
            allocations = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', rec.id),
                ('state', 'in', ['validate']),
                ('holiday_status_id', 'in', annual_leave.ids)
            ])
            for alloc in allocations:
                if alloc.date_from.date() == date or alloc.date_from.date() == date_2:
                    alloc.action_refuse()
                    alloc.action_draft()
                    alloc.number_of_days += rec.reduced_leaves
                    alloc.action_confirm()
                    alloc.action_approve()
                    break
