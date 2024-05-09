# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime as dt


class MaterialTransactionsWizard(models.TransientModel):
    _name = 'material_transactions.wizard'
    _description = 'Material Transactions Wizard'

    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)

    def export_material_transactions(self):
        return self.env.ref('material_transactions_report.id_material_transactions_report').report_action(self)


class ReportVatGetR(models.AbstractModel):
    _name = "report.material_transactions_report.template_mt"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, records):
        for rec in records:
            sheet = workbook.add_worksheet('Stock_Moves')
            format1 = workbook.add_format({'font_size': 14, 'align': 'center', 'bold': True})
            format2 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': False})
            sheet.set_column('A:A', 10)
            sheet.set_column('B:B', 30)
            sheet.set_column('C:C', 10)
            sheet.set_column('D:D', 15)
            sheet.set_column('E:E', 15)
            sheet.set_column('F:F', 15)
            sheet.set_column('G:G', 15)
            sheet.set_column('H:H', 15)
            sheet.set_column('I:I', 15)
            sheet.set_column('J:J', 15)
            sheet.set_column('K:K', 20)
            sheet.set_column('L:L', 20)
            sheet.set_column('M:M', 15)
            sheet.set_column('N:N', 7)
            sheet.set_column('O:O', 7)
            sheet.set_column('P:P', 13)
            row = 0
            sheet.write(row, 0, 'No', format1)
            sheet.write(row, 1, 'Request #', format1)
            sheet.write(row, 2, 'Request Date', format1)
            sheet.write(row, 3, 'Transaction Date', format1)
            sheet.write(row, 4, 'Status', format1)
            sheet.write(row, 5, 'Requester Name', format1)
            sheet.write(row, 6, 'Item Code', format1)
            sheet.write(row, 7, 'Item Description', format1)
            sheet.write(row, 8, 'Quantity Requested', format1)
            sheet.write(row, 9, 'Transaction Quantity', format1)
            sheet.write(row, 10, 'Unit Cost', format1)
            sheet.write(row, 11, 'Total Requested', format1)
            sheet.write(row, 12, 'Project No', format1)
            sheet.write(row, 13, 'Requested Description', format1)
            centione_delivery_request = self.env['centione.delivery.request'].search(
                [('create_date', '>=', rec.date_from), ('create_date', '<=', rec.date_to)])
            no = 0
            for delivery_request in centione_delivery_request.delivery_lines_ids:
                row += 1
                no += 1
                transfer = self.env['stock.picking'].search([('origin', '=', delivery_request.request_id.name)],
                                                            limit=1)
                sheet.write(row, 0, no or "", format2)
                sheet.write(row, 1, transfer.name or delivery_request.request_id.name or "", format2)
                sheet.write(row, 2, str(delivery_request.request_id.create_date or ""), format2)
                # sheet.write(row, 3, 'Request Description', format1)
                sheet.write(row, 3, str(transfer.date_done or ""), format2)
                sheet.write(row, 4, transfer.state or "", format2)
                sheet.write(row, 5, delivery_request.request_id.employee_id.name or "", format2)
                sheet.write(row, 6, delivery_request.product_id.default_code or "", format2)
                sheet.write(row, 7, delivery_request.product_id.name or "", format2)
                sheet.write(row, 8, delivery_request.qty or "", format2)
                sheet.write(row, 9, delivery_request.transfer_qty_done or "", format2)
                if transfer.date_done:
                    unit_cost = delivery_request.product_id.with_context(
                        to_date=transfer.date_done).standard_price
                    sheet.write(row, 10, unit_cost or "", format2)
                else:
                    unit_cost = 0
                    sheet.write(row, 10, "", format2)
                sheet.write(row, 11, unit_cost * delivery_request.qty or "", format2)
                sheet.write(row, 12, delivery_request.request_id.project_id.project_code or "", format2)
                sheet.write(row, 13, delivery_request.request_id.description or "", format2)
