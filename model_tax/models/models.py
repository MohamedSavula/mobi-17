# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    account_move_tax_ids = fields.One2many(comodel_name="account.move.tax", inverse_name="move_id")
    is_send_total_price = fields.Boolean(compute="send_total_price")

    @api.onchange('invoice_line_ids', 'amount_untaxed', 'amount_tax', 'account_move_tax_ids')
    @api.depends('invoice_line_ids', 'amount_untaxed', 'amount_tax', 'account_move_tax_ids')
    def send_total_price(self):
        for rec in self:
            rec.is_send_total_price = False
            if rec.partner_id and not rec.partner_id.petty_cash_holder:
                rec.account_move_tax_ids.update({
                    'untaxed_amount': rec.amount_untaxed,
                    'gross_invoice': rec.amount_total,
                    'net_invoice': rec.amount_untaxed
                })


class AccountMoveTax(models.Model):
    _name = 'account.move.tax'
    _description = "Account Move Tax"

    move_id = fields.Many2one(comodel_name="account.move")
    partner_id = fields.Many2one(comodel_name="res.partner", related="move_id.partner_id", store=True, string="Vendor")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True)
    date = fields.Date(string="WH Date", default=fields.Date.today())
    vendor = fields.Char()
    arabic_name = fields.Char()
    tax_registration = fields.Char()
    vat_number = fields.Char()
    file_number = fields.Char()
    untaxed_amount = fields.Monetary()
    gross_invoice = fields.Float()
    net_invoice = fields.Float()
    wh_tax_type = fields.Char(string='W/H Tax Type')
    tax_description = fields.Char(required=True)
    tax_account_id = fields.Many2one(comodel_name="account.account", required=False)
    amount = fields.Monetary()
    petty_cash_holder = fields.Boolean(related="partner_id.petty_cash_holder", store=True)
    date_move = fields.Date(related="move_id.invoice_date")
    state_invoice = fields.Selection(related="move_id.state")
    year_date = fields.Integer(compute="_compute_year")

    def _compute_year(self):
        for rec in self:
            year = datetime.strptime(str(rec.date_invoice), '%Y-%m-%d').strftime('%Y')
            rec.year_date = year

    @api.onchange('partner_id')
    def get_data_vendor(self):
        for rec in self:
            if rec.partner_id and not rec.partner_id.petty_cash_holder:
                rec.vendor = rec.partner_id.name
                rec.arabic_name = rec.partner_id.arabic_name
                rec.tax_registration = rec.partner_id.petty_tax_registration
                rec.vat_number = rec.partner_id.petty_vat_number
                rec.file_number = rec.partner_id.petty_file_number
                rec.untaxed_amount = rec.move_id.amount_untaxed
                rec.gross_invoice = rec.move_id.amount_tax
                rec.net_invoice = rec.move_id.amount_untaxed
