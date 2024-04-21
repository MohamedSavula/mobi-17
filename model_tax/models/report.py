# -*- coding: utf-8 -*-

from odoo import fields, models, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceLineWizard(models.TransientModel):
    _name = 'account.invoice.tax.wizard'

    year = fields.Selection(string="السنة", selection=[('2019', '2019'),
                                                       ('2020', '2020'),
                                                       ('2021', '2021'),
                                                       ('2022', '2022'),
                                                       ('2023', '2023'),
                                                       ('2024', '2024'),
                                                       ('2025', '2025'),
                                                       ('2026', '2026'),
                                                       ('2027', '2027'),
                                                       ], required=True, )
    duration = fields.Selection(string="المدة", selection=[('الاولى', 'الاولى'),
                                                           ('الثانية', 'الثانية'),
                                                           ('الثالثة', 'الثالثة'),
                                                           ('الرابعة', 'الرابعة'),
                                                           ], required=True, )

    def action_account_invoice_tax_search(self):
        return self.env.ref('model_tax.id_account_invoice_tax_report').report_action(self)


class ReportVatGetR(models.AbstractModel):
    _name = "report.model_tax.template_id_account_invoice_tax_report"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, records):
        for rec in records:
            sheet = workbook.add_worksheet('Account Invoices Report')

            without_borders = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                'font_size': '11',

            })

            font_size_10_center = workbook.add_format(
                {'font_name': 'KacstBook', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                 'border': 1})

            font_size_14_center = workbook.add_format(
                {'font_name': 'KacstBook', 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                 'border': 1})
            font_size_10 = workbook.add_format(
                {'font_name': 'KacstBook', 'font_size': 10, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True,
                 'border': 1})

            font_size_14 = workbook.add_format(
                {'font_name': 'KacstBook', 'font_size': 14, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True,
                 'border': 1})
            table_header_formate = workbook.add_format({
                'bold': 1,
                'border': 1,
                'bg_color': '#AAB7B8',
                'font_size': '10',
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True
            })
            # line 1
            sheet.set_column(0, 0, 10, without_borders)
            sheet.set_column(1, 11, 20, without_borders)
            sheet.merge_range('A1:K1', 'مصلــحـــة الضــــــرائــــــــــب العــــــــامــــــــة', font_size_14_center)

            # line 2
            sheet.set_column(0, 0, 10, without_borders)
            sheet.set_column(1, 11, 20, without_borders)
            # sheet.merge_range('A1:K1', 'رقم المستند     :', font_size_14)
            sheet.merge_range('A2:B2', ' : رقم المستند', font_size_10)
            sheet.write('E2', '( استخدام داخلى )', font_size_14_center)
            sheet.merge_range('F2:K2',
                              '     السيد/ مدير عام الادارة العامه لتجميع نماذج الخصم و الاضافه و التحصيل تحت حساب الضريبه ',
                              font_size_14_center)

            # line 3
            sheet.set_column(0, 0, 10, without_borders)
            sheet.set_column(1, 11, 20, without_borders)
            # sheet.merge_range('A1:K1', 'رقم المستند     :', font_size_14)
            sheet.merge_range('A3:B3', ' : رقم الجهة', font_size_10)

            # line 4
            sheet.set_column(0, 0, 10, without_borders)
            sheet.set_column(1, 11, 20, without_borders)
            # sheet.merge_range('A1:K1', 'رقم المستند     :', font_size_14)
            sheet.merge_range('A4:B4', '  : اسم الجهة', font_size_10)
            sheet.merge_range('C4:D4', 'شركة موبى سيرف', font_size_14)
            sheet.merge_range('F4:K4', '     تحيه طيبه و بعد ،،، ', font_size_14)

            # line 5
            sheet.set_column(0, 0, 10, without_borders)
            sheet.set_column(1, 11, 20, without_borders)
            # sheet.merge_range('A1:K1', 'رقم المستند     :', font_size_14)
            sheet.merge_range('A5:B5', ' : عنوان الجهة', font_size_10)
            sheet.merge_range('C5:D5', '28 شارع 7 المعادي', font_size_14)
            sheet.merge_range('F5:H5', 'مرفق مع هذا ', font_size_14)
            sheet.merge_range('I5:J5', 'بمبلغ :  ', font_size_14)

            # line 6
            sheet.set_column(0, 0, 10, without_borders)
            sheet.set_column(1, 11, 20, without_borders)
            # sheet.merge_range('A1:K1', 'رقم المستند     :', font_size_14)
            sheet.merge_range('A6:B6', ' : كود نوع الجه', font_size_10)
            sheet.merge_range('D6:E6', ' : تليفون الجهة         ', font_size_10)
            # sheet.write('E6', ' : تليفون الجهة         ', font_size_10)
            sheet.merge_range('F6:I6', '  :  فقط وقدرة   ', font_size_14)
            sheet.merge_range('J6:K6', 'رقم التسجيل الضريبي  ', font_size_14)
            # line 7
            sheet.set_column(0, 0, 10, without_borders)
            sheet.set_column(1, 11, 20, without_borders)
            # sheet.merge_range('A1:K1','رقم المستند     :', font_size_14)
            # sheet.write('A4', 'اسم الجهة:', font_size_10)
            sheet.merge_range('C7:E7',
                              '( عام / خاص / اعمال / حكومة / نقابة / نادى / فرع اجنبى / هيئة عامة .......................)',
                              font_size_10)
            sheet.merge_range('F7:H7', ' : الرقم المؤسسي للجهة " الخصم من المنبع " ',
                              font_size_14)
            sheet.write('K7', 'بتاريخ : ' + str(datetime.now().date()), font_size_10)

            # line 9
            sheet.set_column(0, 0, 10, without_borders)
            sheet.set_column(1, 11, 20, without_borders)
            # sheet.merge_range('A1:K1','رقم المستند     :', font_size_14)
            # sheet.write('A4', 'اسم الجهة:', font_size_10)
            # sheet.merge_range('C7:E7', '( عام / خاص / اعمال / حكومة / نقابة / نادى / فرع اجنبى / هيئة عامة .......................)', font_size_10)
            sheet.merge_range('F9:I9', ':  قيمه المبالغ المحصله من الممولين طبقاً للنموذج/ والنماذج المرفقه وعددها ',
                              font_size_10)
            sheet.write('K9', 'نموذج', font_size_14)

            # line 10,11
            sheet.set_column(0, 0, 10, without_borders)
            sheet.set_column(1, 11, 20, without_borders)
            # sheet.merge_range('A1:K1','رقم المستند     :', font_size_14)
            # sheet.write('A4', 'اسم الجهة:', font_size_10)
            # sheet.merge_range('C7:E7', '( عام / خاص / اعمال / حكومة / نقابة / نادى / فرع اجنبى / هيئة عامة .......................)', font_size_10)
            sheet.merge_range('A10:K11',
                              'بيان المحصل تحت حساب الضريبة عن المدة ' + "(" + str(rec.duration) + ")" + 'لسنة' + str(rec.year),
                              font_size_14_center)
            # sheet.write('K7', 'نموذج', font_size_14)

            # header
            sheet.set_column(0, 0, 10, without_borders)
            sheet.set_column(1, 11, 20, without_borders)
            sheet.write('A12', 'م', table_header_formate)
            sheet.write('B12', 'رقم التسجيل الضريبى ', table_header_formate)
            sheet.write('C12', 'رقم الملف', table_header_formate)
            sheet.write('D12', 'اسم الممول', table_header_formate)
            sheet.write('E12', 'العنوان', table_header_formate)
            sheet.write('F12', 'المأموريه ', table_header_formate)
            sheet.write('G12', 'تاريخ التعامل', table_header_formate)
            sheet.write('H12', 'طبيعه التعامل', table_header_formate)
            sheet.write('I12', 'القيمه الاجماليه للتعامل', table_header_formate)
            sheet.write('J12', 'القيمه الصافيه للتعامل', table_header_formate)
            sheet.write('K12', 'النسبه %', table_header_formate)
            sheet.write('L12', 'الضريبة المخصومة', table_header_formate)
            sheet.write('M12', 'الفاتورة', table_header_formate)
            #
            # row = 12
            # row_test = 1
            # col = 0
            # c = 0
            # d = 0
            #
            # for lines in invoices_lines:
            #     sheet.write(row, col, str(row_test) or '', font_size_10)
            #     sheet.write(row, col + 1, lines['tax_registration'] or '', font_size_10)
            #     sheet.write(row, col + 2, lines['file_number'] or '', font_size_10)
            #     sheet.write(row, col + 3, lines['arabic_name'] or '', font_size_10)
            #     sheet.write(row, col + 4, lines['street'] or '', font_size_10)
            #     sheet.write(row, col + 5, lines['tax_office'] or '', font_size_10)
            #     sheet.write(row, col + 6, lines['date_invoice'] or '', font_size_10)
            #     sheet.write(row, col + 7, lines['account_id'] or '', font_size_10)
            #     sheet.write(row, col + 8, str(lines['gross_invoice']) or '', font_size_10)
            #     sheet.write(row, col + 9, str(lines['net_invoice']) or '', font_size_10)
            #     sheet.write(row, col + 10, str(lines['percent']) or '', font_size_10)
            #     sheet.write(row, col + 11, str(lines['with_h_f_payment_test']) or '', font_size_10)
            #     sheet.write(row, col + 12, str(lines['invoice']) or '', font_size_10)
            #     row += 1
            #     row_test += 1
            #
            # workbook.close()
            # output.seek(0)
