# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    apply_manual_currency_exchange = fields.Boolean(string='Apply Manual Currency Exchange')
    manual_currency_exchange_rate = fields.Float(string='Manual Currency Exchange Rate',digits = (12,6))
    active_manual_currency_rate = fields.Boolean('active Manual Currency', default=False, compute="", )
    manual_currency_exchange_rate_x = fields.Float(string='Manual Currency Exchange Rate',digits = (12,6))

    @api.onchange('manual_currency_exchange_rate_x')
    def get_manual_currency_exchange_rate(self):
        for rec in self:
            if rec.manual_currency_exchange_rate_x:
                rec.manual_currency_exchange_rate = 1 / rec.manual_currency_exchange_rate_x
            else:
                rec.manual_currency_exchange_rate = 0

    # def _prepare_invoice(self):
    #   result = super(PurchaseOrder, self)._prepare_invoice()
    #  result.update({
    #     'apply_manual_currency_exchange':self.apply_manual_currency_exchange,
    #    'manual_currency_exchange_rate':self.manual_currency_exchange_rate,
    # })
    # return result

    @api.onchange('company_id', 'currency_id')
    def onchange_currency_id(self):
        if self.company_id or self.currency_id:
            if self.company_id.currency_id != self.currency_id:
                self.active_manual_currency_rate = True
            else:
                self.active_manual_currency_rate = False
        else:
            self.active_manual_currency_rate = False

    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res.update({
            'apply_manual_currency_exchange': self.apply_manual_currency_exchange,
            'manual_currency_exchange_rate': self.manual_currency_exchange_rate,
            'manual_currency_exchange_rate_x': self.manual_currency_exchange_rate_x,
            'active_manual_currency_rate': self.active_manual_currency_rate
        })
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return
        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        # If not seller, use the standard price. It needs a proper currency conversion.
        if not seller:
            # po_line_uom = self.product_uom or self.product_id.uom_po_id
            price_unit = self.env['account.tax']._fix_tax_included_price_company(
                # self.product_id.uom_id._compute_price(self.product_id.standard_price, po_line_uom),
                self.product_id.uom_id._compute_price(self.product_id.standard_price, self.product_id.uom_po_id),
                self.product_id.supplier_taxes_id,
                self.taxes_id,
                self.company_id,
            )
            if price_unit and self.order_id.currency_id and self.order_id.company_id.currency_id != self.order_id.currency_id:
                price_unit = self.order_id.company_id.currency_id._convert(
                    price_unit,
                    self.order_id.currency_id,
                    self.order_id.company_id,
                    self.date_order or fields.Date.today(),
                )
            self.price_unit = price_unit
            # if self.order_id.apply_manual_currency_exchange:
            #   self.price_unit = price_unit * self.order_id.manual_currency_exchange_rate
            # else:
            #   if price_unit and self.order_id.currency_id and self.order_id.company_id.currency_id != self.order_id.currency_id:
            #      price_unit = self.order_id.company_id.currency_id._convert(
            #         price_unit,
            #        self.order_id.currency_id,
            #       self.order_id.company_id,
            #      self.date_order or fields.Date.today(),
            # )

            # self.price_unit = price_unit
            return

        price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price,
                                                                             self.product_id.supplier_taxes_id,
                                                                             self.taxes_id,
                                                                             self.company_id) if seller else 0.0
        if self.order_id.apply_manual_currency_exchange:
            self.price_unit = price_unit * self.order_id.manual_currency_exchange_rate
            return
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id._convert(
                price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        self.price_unit = price_unit

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        if self.order_id.apply_manual_currency_exchange:
            price_unit = self.price_unit / self.order_id.manual_currency_exchange_rate
        return super(PurchaseOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty,
                                                                       product_uom)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_price_unit(self):
        price = super(StockMove, self)._get_price_unit()
        if self.picking_id.purchase_id and self.picking_id.purchase_id.apply_manual_currency_exchange:
            price = self.purchase_line_id.price_unit / self.picking_id.purchase_id.manual_currency_exchange_rate
        return price

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id,
                                       credit_account_id, svl_id, description):

        rslt = super()._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id,
                                                      credit_account_id, svl_id, description)

        if self.picking_id.purchase_id and self.picking_id.purchase_id.apply_manual_currency_exchange:
            new_rslt = {}
            for key, value in rslt.items():
                value["currency_id"] = self.env.company.currency_id.id
                value["amount_currency"] = value["balance"]
                new_rslt[key] = value
            return new_rslt
        return rslt
