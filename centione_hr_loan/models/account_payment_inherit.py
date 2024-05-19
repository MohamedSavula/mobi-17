# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    source_doc = fields.Char(string='Source Document', default=datetime.now().strftime("%Y"))
