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
            locations = rec.locations_ids or self.env['stock.location'].search([('usage', '=', 'internal')])
            products = rec.products_ids or self.env['stock.move.line'].sudo().search(
                    [('date', '>=', rec.from_date), ('date', '<=', rec.to_date), '|',
                     ('location_id', 'in', locations.ids),
                     ('location_dest_id', 'in', locations.ids)]).product_id
            for product in products:
                stock_moves = self.env['stock.move.line'].sudo().search(
                    [('date', '>=', rec.from_date), ('date', '<=', rec.to_date), ('product_id', '=', product.id), '|',
                     ('location_id', 'in', locations.ids),
                     ('location_dest_id', 'in', locations.ids)])
                sheet = workbook.add_worksheet(product.name.replace("'", ""))
                sheet.set_column('A:A', 15)
                sheet.set_column('B:B', 25)
                sheet.set_column('C:C', 25)
                sheet.set_column('D:D', 25)
                sheet.set_column('E:E', 25)
                sheet.set_column('F:F', 15)
                sheet.set_column('G:G', 15)
                sheet.set_column('H:H', 15)
                sheet.set_column('I:I', 15)
                sheet.set_column('J:J', 15)
                stock_quant = self.env['stock.quant'].sudo().search(
                    [('product_id', '=', product.id), ('location_id', 'in', locations.ids)])
                on_hand = sum(stock_quant.mapped('quantity'))
                unit_cost = product.with_context(
                    to_date=rec.from_date).standard_price
                col = 0
                row = 0
                sheet.write(row + 1, col, 'Product Code', format1)
                sheet.write(row + 1, col + 1, product.default_code, format1)
                sheet.write(row + 2, col, 'Product Name', format1)
                sheet.write(row + 2, col + 1, product.name, format1)
                sheet.write(row + 2, col + 4, 'Opening Balance Cost', format1)
                sheet.write(row + 2, col + 5, on_hand * unit_cost, format1)
                # header
                sheet.write(row + 4, col, 'NO', format1)
                sheet.write(row + 4, col + 1, 'Reference', format1)
                sheet.write(row + 4, col + 2, 'From', format1)
                sheet.write(row + 4, col + 3, 'To', format1)
                sheet.write(row + 4, col + 4, 'Transaction Date', format1)
                sheet.write(row + 4, col + 5, 'Partner', format1)
                sheet.write(row + 4, col + 6, 'In Qty', format1)
                sheet.write(row + 4, col + 7, 'Out Qty', format1)
                sheet.write(row + 4, col + 8, 'Balance', format1)
                sheet.write(row + 4, col + 9, 'Actual Cost', format1)
                row = 5
                no = 0
                for stock_move in stock_moves:
                    no += 1
                    col = 0
                    sheet.write(row, col, no, format1)
                    sheet.write(row, col + 1, stock_move.reference, format1)
                    sheet.write(row, col + 2, stock_move.location_id.display_name, format1)
                    sheet.write(row, col + 3, stock_move.location_dest_id.display_name, format1)
                    sheet.write(row, col + 4, str(stock_move.date), format1)
                    sheet.write(row, col + 5, stock_move.picking_id.partner_id.display_name, format1)
                    if stock_move.location_dest_id in locations:
                        on_hand += stock_move.quantity
                        sheet.write(row, col + 6, stock_move.quantity, format1)
                    else:
                        sheet.write(row, col + 6, "", format1)
                    if stock_move.location_id in locations:
                        on_hand -= stock_move.quantity
                        sheet.write(row, col + 7, stock_move.quantity, format1)
                    else:
                        sheet.write(row, col + 7, "", format1)
                    sheet.write(row, col + 8, on_hand, format1)
                    unit_cost = product.with_context(
                        to_date=stock_move.date).standard_price
                    sheet.write(row, col + 9, unit_cost, format1)
                    row += 1
