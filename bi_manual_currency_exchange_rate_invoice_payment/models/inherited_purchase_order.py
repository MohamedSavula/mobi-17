# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    manual_currency_rate = fields.Float('Rate', digits=(12, 6))

    @api.constrains("manual_currency_rate")
    def _check_manual_currency_rate(self):
        for record in self:
            if record.manual_currency_rate_active:
                if record.manual_currency_rate == 0:
                    raise UserError(
                        _('Exchange Rate Field is required , Please fill that.'))

    @api.onchange('manual_currency_rate_active', 'currency_id')
    def check_currency_id(self):
        if self.manual_currency_rate_active:
            if self.currency_id == self.company_id.currency_id:
                self.manual_currency_rate_active = False
                raise UserError(
                    _('Company currency and invoice currency same, You can not add manual Exchange rate for same currency.'))

    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['manual_currency_rate_active'] = self.manual_currency_rate_active
        res['manual_currency_rate'] = self.manual_currency_rate
        return res
