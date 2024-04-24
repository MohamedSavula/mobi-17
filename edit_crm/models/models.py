# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo import models, fields, api


class CrmLeadInh(models.Model):
    _inherit = 'crm.lead'

    expected_cost_la = fields.Monetary('Expected Cost', currency_field='company_currency', tracking=True)
    expected_cost_mi = fields.Monetary('Expected Cost', currency_field='company_currency', tracking=True)
    sales_team_id = fields.Many2one(comodel_name="crm.team", string="", required=False, )
    project_id = fields.Many2one(comodel_name="project.project", string="", required=False, )
    reference_type = fields.Selection(string="", selection=[('vendor_po', 'Vendor Po'), ('loi', 'LOI'),
                                                            ('contract', 'Contract'), ], required=False, )
    reference = fields.Char(string="", required=False, )
    start_date = fields.Date(string="", required=False, )
    end_date = fields.Date(string="", required=False, )
    create_project = fields.Boolean('Create Project')
    is_won = fields.Boolean(related="stage_id.is_won")

    def create_project_button(self):
        for rec in self:
            project = self.env['project.project'].sudo()
            p = project.create({
                "name": rec.name,
                "user_id": rec.env.uid,
                "partner_id": rec.partner_id.id,
                "expected_cost": rec.expected_cost_la,
                "planned_revenue": rec.expected_revenue,
                "create_project": rec.create_project,
                "pipeline_name": rec.name,
                "is_crm_pipe": True,
                "po_type": rec.reference_type,
                "ref_po_type": rec.reference,
                "start_date_po_type": rec.start_date,
                "end_date_po_type": rec.end_date,
            })
            if rec.create_project:
                rec.update({'project_id': p.id})


class ProjectProjectInherit(models.Model):
    _inherit = "project.project"

    expected_cost = fields.Monetary('Expected Cost', currency_field='currency_id', readonly=True)
    planned_revenue = fields.Monetary('Expected Revenue', currency_field='currency_id', readonly=True)
    create_project = fields.Boolean('Create Project', readonly=True)
    pipeline_name = fields.Char('Pipeline Name', readonly=True)
    po_type = fields.Selection([
        ('vendor_po', 'Vendor Po'),
        ('loi', 'LOI'),
        ('contract', 'Contract'),
    ], default='vendor_po', readonly=True)
    ref_po_type = fields.Char('Reference', readonly=True)
    start_date_po_type = fields.Datetime('Start Date', readonly=True)
    end_date_po_type = fields.Datetime('End Date', readonly=True)
    is_crm_pipe = fields.Boolean('Is Come From Crm ', default=False)
    expected_cost_analytic = fields.Monetary(string="Expected Cost")  # related="analytic_account_id.expected_cost"
    planned_revenue_analytic = fields.Monetary(
        string="Planned Revenue")  # related="analytic_account_id.planned_revenue"
    project_code = fields.Char()
    analytic_plan_id = fields.Many2one('account.analytic.plan')
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string="Analytic Tags", related="analytic_account_id.analytic_tag_ids", readonly=False
    )
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'), ('in_progres', 'In Progres'), ('invoiced', 'Invoiced'),
                                        ('locked', 'Locked')], default='draft')

    @api.constrains('project_code')
    def check_char_auto(self):
        for rec in self:
            project_code = self.search(
                [('project_code', '=', rec.project_code),
                 ('project_code', '!=', False), ('id', '!=', rec.id)])
            if project_code:
                raise UserError('Project code duplicated')

    def name_get(self):
        res = []
        for record in self:
            name = "[%s]%s" % (record.project_code or "", record.display_name)
            res.append((record.id, name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, order=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('project_code', '=ilike', name + '%'), ('project_code', operator, name),
                      ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        return self._search(domain + args, limit=limit, order=order)


class AccountAnalyticAccountInherit(models.Model):
    _inherit = 'account.analytic.account'

    expected_cost = fields.Monetary()
    planned_revenue = fields.Monetary()
