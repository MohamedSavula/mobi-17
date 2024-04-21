# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrPreposition(models.Model):
    _name = 'hr.preposition'

    employee_id = fields.Many2one('hr.employee')
    name = fields.Char()
    date_from = fields.Date()
    date_to = fields.Date()
    job = fields.Char()
    department_id = fields.Char('hr.department')
    payment_method = fields.Char()
    bank_name = fields.Char()
    account_number = fields.Char()
    cost_center = fields.Char()
    grade_id = fields.Many2one('hr.grade')
    project = fields.Many2one('project.project', string='Project')
    sub_project = fields.Char()
    cluster_id = fields.Many2one('hr.cluster')
    character_id = fields.Many2one('hr.character')
    title_id = fields.Many2one('hr.title', string="Hr Reference")
    character_level_id = fields.Many2one('hr.character.level', string="Level")
    func_id = fields.Many2one('func.title', string="Functional Title")
