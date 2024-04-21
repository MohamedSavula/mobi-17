# -*- coding: utf-8 -*-

##############################################################################
#
#
#    Copyright (C) 2019-TODAY .
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
##############################################################################

from odoo import models, fields, _


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'
    att_policy_id = fields.Many2one('hr.attendance.policy', string='Attendance Policy')
    late = fields.Float(string="Late",  required=False, )
