# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    end_service_incentive = fields.Integer(string="EoS Months Incentives Per Year",
                                           config_parameter='mobi_hr_character.end_service_incentive')
    is_calculated = fields.Boolean(string="Is Calculated", config_parameter='mobi_hr_character.is_calculated')


class HrTermination(models.Model):
    _name = 'hr.termination'
    _rec_name = 'name'
    _description = 'Termination'
    _order = 'name asc, id desc'

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    name = fields.Char(string="Name", related='employee_id.name')
    department_id = fields.Many2one(comodel_name="hr.department", string="Department")
    job_id = fields.Many2one(comodel_name="hr.job", string="Job Title")
    state = fields.Selection(string="State",
                             selection=[('cancel', 'Cancel'), ('draft', 'Draft'), ('approved', 'Approved'), ],
                             default='draft')
    request_date = fields.Date(string="Request Date")
    approve_date = fields.Date(string="Approve Date")
    termination_date = fields.Date(string="Termination Date")
    reason = fields.Many2one(comodel_name='hr.departure.reason', string='Termination Reason')
    turnover_reason = fields.Many2one(comodel_name="turnover.reason", string="Reason")
    end_incentive = fields.Float(string="End of Service Incentive")
    end_incentive_month = fields.Float(string="End of Service Months",
                                       default=lambda self: self.env["ir.config_parameter"].get_param(
                                           "mobi_hr_character.end_service_incentive"))
    num_custody = fields.Integer(compute='compute_num_custody')
    is_incentive_calc = fields.Boolean(string="Is Incentive Calc",
                                       default=lambda self: self.env["ir.config_parameter"].get_param(
                                           "mobi_hr_character.is_calculated"))
    legal_leaves_incentive = fields.Float()

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.update({'department_id': self.employee_id.department_id.id, 'job_id': self.employee_id.job_id.id})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def get_total_legal_leaves_days(self, employee_id):
        legal_leaves_days = 0
        termination_date = self.termination_date
        leave_types = self.env['hr.leave.type'].search(
            [])
        for it in leave_types:
            if it.end_service_incentive:
                remaining_balance_raw = it.get_days(employee_id.id)
                for rb in remaining_balance_raw:
                    legal_leaves_days += remaining_balance_raw[rb].get('remaining_leaves')
        return legal_leaves_days

    def action_approved(self):
        custody = False
        # check if the employee did not return custody
        # for custody in self.employee_id.employee_custody_ids:
        #     if not custody.return_date:
        #         custody = True
        #         raise ValidationError(_('Please Check The Custody Of This Employee'))

        if 'hr.loan' in self.env:
            loans = self.env['hr.loan'].search([('employee_id', '=', self.employee_id.id)])
            for loan in loans:
                if loan.total_unpaid != 0:
                    raise ValidationError(_('Please Check The Loans Of This Employee'))

        # self.employee_id.state = 'terminated'
        wage_per_day = self.employee_id.contract_id.wage / 30.0
        # legal_leaves_days = self.get_total_legal_leaves_days(self.employee_id)
        legal_leaves_days = self.employee_id.leaves_count

        self.legal_leaves_incentive = wage_per_day * legal_leaves_days
        self.end_incentive += self.legal_leaves_incentive

        # cancel all employee's contracts
        self.employee_id.contract_id.date_end = self.termination_date
        # self.employee_id.contract_id.end_incentive = self.end_incentive

        for contract in self.employee_id.contract_ids:
            if contract.state != 'cancel' and contract.state != 'close':
                if contract.date_end and contract.date_end > self.termination_date:
                    contract.date_end = self.termination_date
                contract.state = 'cancel'
                contract.end_incentive = self.end_incentive
                contract.end_incentive_month = self.end_incentive_month
        return self.write({'state': 'approved', 'approve_date': fields.Date.today()})

    # def action_custody(self):
    #     ids = self.employee_id.employee_custody_ids.ids
    #     return {
    #         'name': "Employee Custody",
    #         'view_type': 'form',
    #         'view_mode': 'tree,form',
    #         'res_model': 'hr.custody',
    #         'type': 'ir.actions.act_window',
    #         'domain': [("id", "in", ids)],
    #         'context': {'default_employee_id': self.employee_id.id},
    #     }

    def compute_num_custody(self):
        for rec in self:
            rec.num_custody = rec.num_custody#len(rec.employee_id.employee_custody_ids)
