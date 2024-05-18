# -*- coding: utf-8 -*-

from odoo import models, fields


class ReportItemCard(models.TransientModel):
    _name = 'report.item.card'
    _description = 'Report Item Card'

    from_date = fields.Date()
    products_ids = fields.Many2many(comodel_name="product.product")
    to_date = fields.Date(default=fields.Date.today)
    locations_ids = fields.Many2many(comodel_name="stock.location")

    def action_print(self):
        return self.env.ref('report_item_card.id_report_item_card').report_action(self)


class ProjectTaskPrintEducational(models.AbstractModel):
    _name = "report.report_item_card.id_report_item_card_template"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, records):
        for rec in records:
            format1 = workbook.add_format(
                {'font_size': 11, 'align': 'center', 'bold': True, 'border': True,
                 'color': 'black'})

            format3 = workbook.add_format(
                {'font_size': 11, 'align': 'center', 'bold': True, 'border': True, 'bg_color': '#ffd966',
                 'color': 'black'})
            format4 = workbook.add_format(
                {'font_size': 11, 'align': 'center', 'bold': True, 'border': True, 'bg_color': '#a4c2f4',
                 'color': 'black'})
            format2 = workbook.add_format(
                {'font_size': 11, 'align': 'center', 'bold': True, 'border': True, 'bg_color': '#0000ff',
                 'color': '#ffffff',
                 })
            sheet = workbook.add_worksheet("Transfer report")
            sheet.set_column('A:A', 25)
            sheet.set_column('B:B', 25)
            col = 1
            row = 1
            sheet.merge_range(0, 0, 0, 5, 'Alexandria Governorate', format1)
            sheet.write(6, col, 'Total', format3)
