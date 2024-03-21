# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class purchaseamountuser(models.Model):
    _name = "purchase.amount.user"

    user_id = fields.Many2one("res.users")
    _1st_approver = fields.Many2one(comodel_name='res.users',string="1st Approver")
    _2st_approver = fields.Many2one(comodel_name='res.users',string="2nd Approver")
    _3st_approver = fields.Many2one(comodel_name='res.users',string="3rd Approver")
    _4st_approver = fields.Many2one(comodel_name='res.users',string="4th Approver")
    _5st_approver = fields.Many2one(comodel_name='res.users',string="5th Approver")
    amount_max = fields.Float("Amount Max")
    amount_min = fields.Float("Amount Min")
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency", required=True)
