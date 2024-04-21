from odoo import models, fields, api


class HrPenalty(models.Model):
    _name = 'hr.penalty'

    penalty_id = fields.Many2one('hr.employee')
    penalty_type = fields.Char('Type')
    penalty_date = fields.Datetime('Date')
    penalty_desc = fields.Text('Description')
    penalty_action = fields.Text('Actions')
    penalty_deduct_days = fields.Float('Deduction Days')
    penalty_deduct_type = fields.Selection(string="Deduction Type",
                                           selection=[('amount', 'Amount'), ('days', 'Days'), ])
    penalty_site = fields.Char('Penalty Site')
    penalty_note = fields.Text('Notes')
    responsible_employee_id = fields.Many2one('hr.employee')
