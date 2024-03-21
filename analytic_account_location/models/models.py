# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class StockLocationInherit(models.Model):
    _inherit = 'stock.location'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          related="location_dest_id.analytic_account_id", store=True)
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string="Analytic Tags"
    )

    # def _action_done(self):
    #     date_done = self.date_done
    #     res = super()._action_done()
    #     self.write({'date_done': date_done})
    #     return res
    #
    # def button_validate(self):
    #     res = super().button_validate()
    #     for rec in self:
    #         if rec.date_done:
    #             self.env['account.move'].search([('stock_move_id', '!=', False)]).filtered(
    #                 lambda l: rec.name in l.ref).sudo().write({'date': rec.date_done.date()})
    #     return res


# class StockMoveInherit(models.Model):
#     _inherit = 'stock.move'
#
#     date = fields.Datetime(
#         'Date', index=True, required=False,
#         states={'done': [('readonly', True)]}, related='picking_id.date_done', store=True,
#         help="Move date: scheduled date until move is done, then date of actual move processing")


# class StockMoveLineInherit(models.Model):
#     _inherit = 'stock.move.line'
#
#     date = fields.Datetime('Date', required=False, related='picking_id.date_done', store=True)


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    project_id = fields.Many2one(comodel_name="project.project", string="Project")
    wip_location_id = fields.Many2one('stock.location', "WIP Location")
    cost_location_id = fields.Many2one('stock.location', "COST Location")
    project_code = fields.Char()
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

    def in_progres(self):
        for rec in self:
            rec.state = "in_progres"
            if rec.project_id:
                rec.project_id.state = 'in_progres'

    def invoiced(self):
        for rec in self:
            rec.state = "invoiced"
            if rec.project_id:
                rec.project_id.state = 'invoiced'

    def locked(self):
        for rec in self:
            rec.state = "locked"
            if rec.project_id:
                rec.project_id.state = 'locked'

    @api.constrains('project_id')
    def _unique_project_id(self):
        for rec in self:
            if rec.project_id:
                account_analytic_account = self.env['account.analytic.account'].search(
                    [('id', '!=', rec.id),
                     ('project_id', '=', rec.project_id.id),
                     ('project_id', '!=', False)])
                if len(account_analytic_account) > 0:
                    raise ValidationError(_('Another Analytic Account Have This Project'))


class ProjectProjectInherit(models.Model):
    _inherit = 'project.project'

    is_created_analytic = fields.Boolean(copy=False)

    def create_analytic_account(self):
        for rec in self:
            account_analytic_account = self.env['account.analytic.account']
            account_account = self.env['account.account'].search([('code', '=', '100801001')])
            account_account1 = self.env['account.account'].search([('code', '=', '500101001')])
            analytic_id = account_analytic_account.create({
                'name': rec.name,
                'partner_id': rec.partner_id.id,
                'project_id': rec.id,
                'project_code': rec.project_code,
                'plan_id': rec.analytic_plan_id.id if rec.analytic_plan_id else 14,
                'analytic_tag_ids': rec.analytic_tag_ids.ids,
                'expected_cost': rec.expected_cost,
                'planned_revenue': rec.planned_revenue,
                'code': rec.project_code,
            })
            wip_loc = self.env['stock.location'].create({
                'name': 'WIP ' + rec.name,
                'usage': 'inventory',
                'analytic_account_id': analytic_id.id,
                'valuation_in_account_id': account_account.id,
                'valuation_out_account_id': account_account.id,
            })
            cost_loc = self.env['stock.location'].create({
                'name': 'COST ' + rec.name,
                'usage': 'inventory',
                'analytic_account_id': analytic_id.id,
                'valuation_in_account_id': account_account1.id,
                'valuation_out_account_id': account_account1.id,
            })
            analytic_id.write({
                'wip_location_id': wip_loc.id,
                'cost_location_id': cost_loc.id,
            })
            rec.analytic_account_id = analytic_id.id
            rec.is_created_analytic = True
