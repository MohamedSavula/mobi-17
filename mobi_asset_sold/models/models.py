# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    ref_sold = fields.Char(string="Reference")
    sold_date = fields.Date(default=fields.Date.today)
    is_sold = fields.Boolean()

    def set_to_close(self, invoice_line_ids, date=None, message=None):
        res = super().set_to_close(invoice_line_ids, date=date, message=message)
        full_asset = self + self.children_ids
        for asset in full_asset:
            if invoice_line_ids:
                asset.is_sold = True
                asset.sold_date=fields.Date.today()
        return res
    vendor_id = fields.Many2one(comodel_name="res.partner" ,compute="get_vendor")



    @api.depends('original_move_line_ids')
    def get_vendor(self):
        for rec in self:
            rec.vendor_id=False
            if rec.original_move_line_ids:
                rec.vendor_id=rec.original_move_line_ids[0].partnet_id.id

