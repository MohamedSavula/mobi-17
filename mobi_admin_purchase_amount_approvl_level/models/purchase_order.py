# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class PowerConfiguration(models.Model):
    _name = 'power.configuration'
    _description = 'Power Configuration'

    name = fields.Char(string="Name", required=True)


class VendorType(models.Model):
    _name = 'vendor.type'
    _description = 'Vendor Type'

    name = fields.Char(string="Name", required=True)


class PartnerOffice(models.Model):
    _name = 'partner.office'
    _description = 'Partner Office'

    name = fields.Char(string="Name", required=True)


class ContactAccountLine(models.Model):
    _name = 'contact.account.line'
    _description = 'Contact Account Line'

    partner_id = fields.Many2one(comodel_name="res.partner")
    account_id = fields.Many2one(comodel_name="account.account", string="Name", required=True)
    is_approved = fields.Boolean()


class AccountAccountInherit(models.Model):
    _inherit = 'account.account'

    is_customer = fields.Boolean(copy=False)
    is_vendor = fields.Boolean(copy=False)
    petty_cash_holder = fields.Boolean(copy=False)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    job_position = fields.Char(string='Job Position')
    arabic_name = fields.Char(string="Arabic Name")
    fax = fields.Char(string="Fax")
    tax_office = fields.Char(string="Tax Office")
    power_configuration_id = fields.Many2one(comodel_name="power.configuration", string="Power Configuration")
    office_id = fields.Many2one(comodel_name="partner.office", string="Office")
    vendor_type_id = fields.Many2one(comodel_name="vendor.type", string="Vendor Type")
    tax_registration = fields.Char(string="Tax Registration")
    vat_number = fields.Char(string="Vat Number")
    file_number = fields.Char(string="File Office")
    is_employee = fields.Boolean()
    petty_cash_holder = fields.Boolean()
    petty_tax_registration = fields.Char(string="Tax Registration")
    petty_vat_number = fields.Char(string="Vat Number")
    petty_file_number = fields.Char(string="File Office")
    contact_line_ids = fields.One2many(comodel_name="contact.account.line", inverse_name="partner_id")
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal",
                                 domain="[('type', 'in', ['sale', 'purchase'])]")

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.customer_rank > 0:
            accounts = self.env['account.account'].sudo().search([('is_customer', '=', True)])
            res.contact_line_ids = [(0, 0, {
                'partner_id': res.id,
                'account_id': account.id,
            }) for account in accounts]
        elif res.supplier_rank > 0:
            if not res.petty_cash_holder:
                accounts = self.env['account.account'].sudo().search([('is_vendor', '=', True)])
                res.contact_line_ids = [(0, 0, {
                    'partner_id': res.id,
                    'account_id': account.id,
                }) for account in accounts]
            elif res.petty_cash_holder:
                accounts = self.env['account.account'].sudo().search([('petty_cash_holder', '=', True)])
                res.contact_line_ids = [(0, 0, {
                    'partner_id': res.id,
                    'account_id': account.id,
                }) for account in accounts]
        return res

    @api.constrains('vat')
    def check_vat_number(self):
        for rec in self:
            vat = self.search(
                [('vat', '=', rec.vat),
                 ('vat', '!=', False), ('id', '!=', rec.id), ('id', '!=', rec.parent_id.id)])
            if vat:
                raise UserError('tax registration duplicate')
            vat_number = self.search(
                [('vat_number', '=', rec.vat_number),
                 ('vat_number', '!=', False), ('id', '!=', rec.id), ('id', '!=', rec.parent_id.id)])
            if vat_number:
                raise UserError('Vat number duplicate')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approve_date = fields.Datetime(string="Approve Date", required=False, )
    purchase_review_log_ids = fields.One2many('purchase.review.log', 'order_id')
    filted_purchase_log = fields.Many2many('purchase.review.log', compute='compute_filtered_log')
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('1st_approve', '1st Approved'),
        ('2nd_approve', '2nd Approved'),
        ('3rd_approve', '3rd Approved'),
        ('4th_approve', '4th Approved'),
        ('5th_approve', '5th Approved'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft')
    purchase_amount_user_id = fields.Many2one(comodel_name="purchase.amount.user", readonly=False,
                                              compute="get_purchase_amount_user_id", store=True)
    # user_id = fields.Many2one(related="purchase_amount_user_id.user_id", store=True)
    _1st_approver = fields.Many2one(related="purchase_amount_user_id._1st_approver", store=True,
                                    comodel_name='res.users')
    is_1st_approver = fields.Boolean(compute="check_is_1st_approver")
    _2st_approver = fields.Many2one(related="purchase_amount_user_id._2st_approver", store=True,
                                    comodel_name='res.users')
    is_2st_approver = fields.Boolean(compute="check_is_2st_approver")
    _3st_approver = fields.Many2one(related="purchase_amount_user_id._3st_approver", store=True,
                                    comodel_name='res.users')
    is_3st_approver = fields.Boolean(compute="check_is_3st_approver")
    _4st_approver = fields.Many2one(related="purchase_amount_user_id._4st_approver", store=True,
                                    comodel_name='res.users')
    is_4st_approver = fields.Boolean(compute="check_is_4st_approver")
    _5st_approver = fields.Many2one(related="purchase_amount_user_id._5st_approver", store=True,
                                    comodel_name='res.users')
    is_5st_approver = fields.Boolean(compute="check_is_5st_approver")

    @api.depends('name')
    def check_is_1st_approver(self):
        for rec in self:
            rec.is_1st_approver = False
            if self.env.user.id == rec._1st_approver.id:
                rec.is_1st_approver = True

    @api.depends('name')
    def check_is_2st_approver(self):
        for rec in self:
            rec.is_2st_approver = False
            if self.env.user.id == rec._2st_approver.id:
                rec.is_2st_approver = True

    @api.depends('name')
    def check_is_3st_approver(self):
        for rec in self:
            rec.is_3st_approver = False
            if self.env.user.id == rec._3st_approver.id:
                rec.is_3st_approver = True

    @api.depends('name')
    def check_is_4st_approver(self):
        for rec in self:
            rec.is_4st_approver = False
            if self.env.user.id == rec._4st_approver.id:
                rec.is_4st_approver = True

    @api.depends('name')
    def check_is_5st_approver(self):
        for rec in self:
            rec.is_5st_approver = False
            if self.env.user.id == rec._5st_approver.id:
                rec.is_5st_approver = True

    @api.depends('amount_total')
    def get_purchase_amount_user_id(self):
        for rec in self:
            rec.purchase_amount_user_id = self.env['purchase.amount.user'].sudo().search(
                [('amount_min', '<=', rec.amount_total), ('amount_max', '>=', rec.amount_total),
                 ('currency_id', '=', rec.currency_id.id), ], limit=1).id

    def create_log_approval(self):
        self.env['purchase.review.log'].create({
            'user_id': self.env.user.id,
            'job_position': self.env.user.partner_id.job_position,
            'review_status': self.state,
            'date': fields.Datetime.now(),
            'order_id': self.id})

    def button_1st_approver(self):
        for rec in self:
            if rec._1st_approver:
                rec.state = "1st_approve"
            else:
                rec.button_confirm()
            rec.create_log_approval()

    def button_2st_approver(self):
        for rec in self:
            if rec._2st_approver:
                rec.state = "2nd_approve"
            else:
                rec.button_confirm()
            rec.create_log_approval()

    def button_3st_approver(self):
        for rec in self:
            if rec._3st_approver:
                rec.state = "3rd_approve"
            else:
                rec.button_confirm()
            rec.create_log_approval()

    def button_4st_approver(self):
        for rec in self:
            if rec._4st_approver:
                rec.state = "4th_approve"
            else:
                rec.button_confirm()
            rec.create_log_approval()

    def button_5st_approver(self):
        for rec in self:
            if rec._5st_approver:
                rec.state = "5th_approve"
            else:
                rec.button_confirm()
            rec.create_log_approval()

    @api.depends('purchase_review_log_ids')
    def compute_filtered_log(self):
        for rec in self:
            rec.filted_purchase_log = rec.purchase_review_log_ids.ids

    def button_confirm(self):
        self.update({
            'state': 'draft'
        })
        return super().button_confirm()
