# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OpenDate(models.Model):
    _name = 'open.date'
    _description = 'Open Date'

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    journal_entries_start_date = fields.Date(related="company_id.journal_entries_start_date", readonly=False)
    journal_entries_end_date = fields.Date(related="company_id.journal_entries_end_date", readonly=False)
    all_users_start_date = fields.Date(related="company_id.all_users_start_date", readonly=False)
    all_users_end_date = fields.Date(related="company_id.all_users_end_date", readonly=False)


class ResConfigSettingsInherit(models.TransientModel, ):
    _inherit = 'res.config.settings'

    journal_entries_start_date = fields.Date(related="company_id.journal_entries_start_date", readonly=False)
    journal_entries_end_date = fields.Date(related="company_id.journal_entries_end_date", readonly=False)
    all_users_start_date = fields.Date(related="company_id.all_users_start_date", readonly=False)
    all_users_end_date = fields.Date(related="company_id.all_users_end_date", readonly=False)
    documents_product_settings = fields.Boolean(related='company_id.documents_product_settings', readonly=False,
                                                string="Product")
    product_folder = fields.Many2one('documents.folder', related='company_id.product_folder', readonly=False,
                                     string="product default workspace")
    product_tags = fields.Many2many('documents.tag', 'product_tags_table',
                                    related='company_id.product_tags', readonly=False,
                                    string="Product Tags")

    @api.onchange('product_folder')
    def on_product_folder_change(self):
        if self.product_folder != self.product_tags.mapped('folder_id'):
            self.product_tags = False


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    journal_entries_start_date = fields.Date()
    journal_entries_end_date = fields.Date()
    all_users_start_date = fields.Date()
    all_users_end_date = fields.Date()
    documents_product_settings = fields.Boolean()
    product_folder = fields.Many2one('documents.folder',
                                     string="product default workspace")
    product_tags = fields.Many2many('documents.tag', 'product_tags_table',
                                    string="Product Tags")


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        res.constrains_open_date()
        return res

    def write(self, vals):
        res = super().write(vals)
        self.constrains_open_date()
        return res

    @api.constrains('date')
    def constrains_open_date(self):
        for rec in self:
            if rec.company_id.all_users_start_date and rec.company_id.all_users_end_date:
                if not rec.company_id.all_users_end_date >= rec.date >= rec.company_id.all_users_start_date:
                    raise UserError(_('You cannot set a lock date in the future.'))
            elif rec.company_id.journal_entries_start_date and rec.company_id.journal_entries_end_date and self.user_has_groups(
                    'account.group_account_manager'):
                if not rec.company_id.journal_entries_end_date >= rec.date >= rec.company_id.journal_entries_start_date:
                    raise UserError(_('You cannot set a lock date in the future.'))
