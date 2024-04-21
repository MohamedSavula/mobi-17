# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAssetInherit(models.Model):
    _inherit = 'account.asset'

    asset_disposal_gain_account_id = fields.Many2one(comodel_name="account.account",
                                                     string="Asset Disposal Gain Account")
    asset_disposal_loss_account_id = fields.Many2one(comodel_name="account.account",
                                                     string="Asset Disposal Loss Account")
