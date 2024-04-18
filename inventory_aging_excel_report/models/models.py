# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import xlsxwriter
from io import BytesIO
import base64
from datetime import datetime


class ExcelReport(models.TransientModel):
    _name = 'report.excel'

    excel_file = fields.Binary('Download report Excel', attachment=True, readonly=True)
    file_name = fields.Char('Excel File', size=64)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price = fields.Float()
    internal_qty = fields.Float()
    picking_date_done = fields.Datetime()
    picking_date_issuance = fields.Datetime()
    po_currency_id = fields.Many2one('res.currency')
    days = fields.Integer()
    moving_type = fields.Selection(selection=[('From 0 To 30', 'From 0 To 30'),
                                              ('From 31 To 60', 'From 31 To 60'),
                                              ('From 61 To 120', 'From 61 To 120'),
                                              ('From 121 To 180', 'From 121 To 180'),
                                              ('From 181 To 270', 'From 181 To 270'),
                                              ('From 271 To 365', 'From 271 To 365'),
                                              ('1-2 year', '1-2 year'),
                                              ('more than 2 years', 'more than 2 years'),
                                              ])
    qty_last_year = fields.Float()
    unit_cost_price = fields.Float()
    aging = fields.Integer()
    movable_within_one_year = fields.Boolean()
    slow_moving_1to2_years = fields.Boolean()
    scrab_more_than2years = fields.Boolean()


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    usage = fields.Selection(related='location_id.usage')


class AccountMoveLine(models.Model):
    _inherit = 'stock.move.line'

    picking_code = fields.Selection(related='picking_id.picking_type_id.code')
    is_internal_location = fields.Boolean(related='location_id.is_internal_location')
    is_vendor_location = fields.Boolean(related='location_dest_id.is_internal_location')
    date_done = fields.Datetime(related='picking_id.date_done')


class InventoryAgingWizard(models.TransientModel):
    _name = 'inventory.aging.wizard'

    excel_file = fields.Binary('Download report Excel', attachment=True, readonly=True)
    file_name = fields.Char('Excel File', size=64)
    date = fields.Date(required=True, default=fields.Date.context_today)

    def action_inventory_aging_search(self):
        lines = []
        # my_products = self.env['product.product'].search([('type', '=', 'product')])
        # my_products1 = self.env['product.product'].search_count([('type', '=', 'product')])
        # print('all products > ', my_products1)
        products = []
        move_product = self.env['account.move.line'].search([
            ('account_id.code', '=', '100700002'),
            ('product_id', '!=', False),
            ('date', '<=', self.date),
        ])
        products_move = move_product.mapped('product_id')

        # product_stocks = []
        # stock_inventory = self.env['stock.inventory'].search([('id', '=', 7)])
        # for stock in stock_inventory.move_ids:
        #     product_stocks.append(stock.product_id)
        product_stock_move = self.env['stock.move'].search([], order='id asc')
        product_stocks = product_stock_move.mapped('product_id')
        # print('product_stocks >> ', product_stocks)
        all_product = []
        for product in product_stocks:
            all_product.append(product)
        for product in products_move:
            all_product.append(product)
        # print('all_product >> ', all_product)
        all_product_set = list(set(all_product))
        # print(len(all_product_set))
        for prod in all_product_set:
            prod.moving_type = ''
            prod.days = ''
            prod.price = ''
            prod.unit_cost_price = ''
            # prod.standard_price = ''
            prod.picking_date_done = ''
            prod.picking_date_issuance = ''
            prod.po_currency_id = ''
            prod.qty_last_year = ''
            prod.aging = ''
            prod.movable_within_one_year = ''
            prod.slow_moving_1to2_years = ''
            prod.scrab_more_than2years = ''
            prod.internal_qty = 0
            # print('in loop')
            qty_in = 0
            qty_out = 0
            moves_in = self.env['stock.move.line'].search([
                ('product_id', '=', prod.id),
                ('state', '=', 'done'),
                ('date', '<=', self.date),
                ('location_dest_id.is_internal_location', '=', True)
            ])
            for move in moves_in:
                qty_in += move.qty_done
            moves_out = self.env['stock.move.line'].search([
                ('product_id', '=', prod.id),
                ('state', '=', 'done'),
                ('date', '<=', self.date),
                ('location_id.is_internal_location', '=', True)
            ])
            for move in moves_out:
                qty_out += move.qty_done
            internal_qty = qty_in - qty_out
            prod.internal_qty = internal_qty
            # if internal_qty > 0:
            products.append(prod)

        for prod in products:
            prl = self.env['purchase.order.line'].search([
                ('order_id.date_order', '<=', self.date),
                ('product_id', '=', prod.id)], order="id desc", limit=1)
            prod.price = prl.price_unit
            prod.po_currency_id = prl.currency_id.id

            ################################################
            if prod in product_stocks:
                stock_move = self.env['stock.move'].search([
                    ('product_id', '=', prod.id)
                ], limit=1)
                unit_cost_price = stock_move.price_unit
                quantity = stock_move.quantity
                value = quantity * unit_cost_price
                account_move_line = self.env['account.move.line'].search([
                    ('account_id.code', '=', '100700002'),
                    ('product_id', '=', prod.id),
                    ('date', '<=', self.date),
                ])
                if account_move_line:
                    for line in account_move_line:
                        value += line.balance
                        quantity += line.quantity
                    if quantity > 0:
                        prod.unit_cost_price = value / quantity
                    else:
                        prod.unit_cost_price = unit_cost_price
                else:
                    prod.unit_cost_price = unit_cost_price
            else:
                quantity = 0
                value = 0
                account_move_line = self.env['account.move.line'].search([
                    ('account_id.code', '=', '100700002'),
                    ('product_id', '=', prod.id),
                    ('date', '<=', self.date),
                ])
                if account_move_line:
                    for line in account_move_line:
                        value += line.balance
                        quantity += line.quantity
                    if quantity > 0:
                        prod.unit_cost_price = value / quantity
                else:
                    prod.unit_cost_price = 0

            cost_change = self.env['cost.change'].search([
                ('cost_product_id', '=', prod.id), ('change_date', '<=', self.date)
            ], order='change_date desc', limit=1)
            if cost_change:
                prod.standard_price = cost_change.cost_value
            else:
                prod.standard_price = prod.standard_price

            ###############################################
            stock_move_line = self.env['stock.move.line'].search([
                ('product_id', '=', prod.id),
                ('state', '=', 'done'),
                ('picking_code', '=', 'incoming'),
                ('date', '<=', self.date)
            ], order="id desc", limit=1)
            if stock_move_line.date_done:
                prod.picking_date_done = stock_move_line.date_done

            if stock_move_line:
                date_format = '%Y-%m-%d'
                b = datetime.strptime(str(self.date), date_format)
                a = datetime.strptime(str(stock_move_line.date_done.date()), date_format)
                delta = b - a

                prod.aging = delta.days  # that's it`

            stock_move_line1 = self.env['stock.move.line'].search([
                ('product_id', '=', prod.id),
                ('state', '=', 'done'),
                ('picking_code', '=', 'internal'),
                ('date', '<=', self.date)
            ], order="id desc", limit=1)
            if stock_move_line1.date_done:
                prod.picking_date_issuance = stock_move_line1.date_done

            if stock_move_line1:
                date_format = '%Y-%m-%d'
                b1 = datetime.strptime(str(fields.Datetime.today().date()), date_format)
                a1 = datetime.strptime(str(stock_move_line1.date_done.date()), date_format)
                delta1 = b1 - a1

                prod.days = delta1.days  # that's it

                if 0 <= delta1.days <= 30:
                    prod.moving_type = 'From 0 To 30'
                    prod.movable_within_one_year = True

                elif 31 <= delta1.days <= 60:
                    prod.moving_type = 'From 31 To 60'
                    prod.movable_within_one_year = True

                elif 61 <= delta1.days <= 120:
                    prod.moving_type = 'From 61 To 120'
                    prod.movable_within_one_year = True

                elif 121 <= delta1.days <= 188:
                    prod.moving_type = 'From 121 To 180'
                    prod.movable_within_one_year = True

                elif 181 <= delta1.days <= 270:
                    prod.moving_type = 'From 181 To 270'
                    prod.movable_within_one_year = True

                elif 271 <= delta1.days <= 365:
                    prod.moving_type = 'From 271 To 365'
                    prod.movable_within_one_year = True

                elif 366 <= delta1.days <= 730:
                    prod.moving_type = '1-2 year'
                    prod.slow_moving_1to2_years = True

                elif delta1.days > 730:
                    prod.moving_type = 'more than 2 years'
                    prod.scrab_more_than2years = True

            stock_move_line_last_year = []
            qty = 0

            stock_move_line_all_year = self.env['stock.move.line'].search([
                ('product_id', '=', prod.id),
                ('state', '=', 'done'),
                ('picking_code', '=', 'internal'),
                ('date', '<=', self.date)
            ])

            year = datetime.strptime(str(fields.Datetime.today()), '%Y-%m-%d %H:%M:%S').strftime('%Y')
            year = int(year) - 1

            for mov in stock_move_line_all_year:
                move_year = datetime.strptime(str(mov.date_done), '%Y-%m-%d %H:%M:%S').strftime('%Y')
                if str(year) == str(move_year):
                    stock_move_line_last_year.append(mov)
            for mov1 in stock_move_line_last_year:
                qty += mov1.qty_done
            prod.qty_last_year = qty

        # -------------------------------------------------------------#
        if products:
            for product in products:
                if product.internal_qty > 0:
                    lines.append(product)

            act = self.generate_excel(lines, all_product)

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'report.excel',
                'res_id': act.id,
                'view_mode': 'form',
                'context': self.env.context,
                'target': 'new',
            }

        else:
            raise UserError(_('No Item for This '))

    def generate_excel(self, product_ids, all_product):

        filename = 'Inventory Aging Report'

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Inventory Aging Excel')
        testing = workbook.add_worksheet('Testing')

        without_borders = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': '11',

        })

        font_size_10 = workbook.add_format(
            {'font_name': 'KacstBook', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
             'border': 1})
        # font_size_20 = workbook.add_format(
        #     {'font_name': 'KacstBook', 'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
        #      'bold': True, 'border': 1})

        table_header_formate = workbook.add_format({
            'bold': 1,
            'border': 1,
            'bg_color': '#AAB7B8',
            'font_size': '10',
            # 'height': '20px',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        # new with gamal tasks by thomas
        total_value_new = 0
        for product in product_ids:
            total_value_new+= product.internal_qty * product.unit_cost_price
        total_line_items = sum(self.env['account.move.line'].search([
            ('account_id.code', '=', '100700002'),
            ('date', '<=', self.date),
        ]).mapped("balance"))
        difference_total = total_line_items - total_value_new
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 11, 20)
        sheet.write('A1', 'No', table_header_formate)
        sheet.write('B1', 'code', table_header_formate)  # Done
        sheet.write('C1', 'name', table_header_formate)  # Done
        sheet.write('D1', 'Unit Cost Source Currency', table_header_formate)
        sheet.write('E1', 'Purchase Currency', table_header_formate)
        sheet.write('F1', 'Unit Cost', table_header_formate)
        sheet.write('G1', 'On Hand Quantity', table_header_formate)
        sheet.write('H1', 'Total Value', table_header_formate)
        sheet.write('I1', 'Date of Last Addition Transaction', table_header_formate)
        sheet.write('J1', 'Last Issuance Transaction Date', table_header_formate)
        sheet.write('K1', 'Days', table_header_formate)
        sheet.write('L1', 'Moving Type', table_header_formate)
        sheet.write('M1', 'Last year consumption', table_header_formate)
        sheet.write('N1', 'Aging', table_header_formate)
        sheet.write('O1', 'Movable Within One Year', table_header_formate)
        sheet.write('P1', 'Slow Moving 1 to 2 Years', table_header_formate)
        sheet.write('Q1', 'Scrab More Than 2 Years', table_header_formate)
        sheet.write('R1', 'Cost Log', table_header_formate)
        sheet.write('S1', 'Sales Price', table_header_formate)
        sheet.write('T1', 'Cost', table_header_formate)

        row = 1
        col = 0
        # balance = 0
        #new by thomas
        for product in product_ids:
            percentage_value = 0
            if total_value_new > 0 :
                percentage_value = (product.internal_qty * product.unit_cost_price)/total_value_new

            value_in_case = percentage_value * difference_total
            unit_div = value_in_case/product.internal_qty
            new_unit_cost = product.unit_cost_price + unit_div
            sheet.write(row, col, str(row) or '', font_size_10)
            sheet.write(row, col + 1, product.default_code or '', font_size_10)
            sheet.write(row, col + 2, product.name or '', font_size_10)
            sheet.write(row, col + 3, product.price or '', font_size_10)
            sheet.write(row, col + 4, product.po_currency_id.name or '', font_size_10)
            sheet.write(row, col + 5, round(new_unit_cost,5), font_size_10)
            sheet.write(row, col + 6, product.internal_qty, font_size_10)
            sheet.write(row, col + 7, round(product.internal_qty * new_unit_cost,5), font_size_10)
            sheet.write(row, col + 8, str(product.picking_date_done or ''), font_size_10)
            sheet.write(row, col + 9, str(product.picking_date_issuance or ''), font_size_10)
            sheet.write(row, col + 10, product.days or '', font_size_10)
            sheet.write(row, col + 11, product.moving_type or '', font_size_10)
            sheet.write(row, col + 12, product.qty_last_year, font_size_10)
            sheet.write(row, col + 13, product.aging, font_size_10)
            sheet.write(row, col + 14, product.movable_within_one_year or '', font_size_10)
            sheet.write(row, col + 15, product.slow_moving_1to2_years or '', font_size_10)
            sheet.write(row, col + 16, product.scrab_more_than2years or '', font_size_10)
            sheet.write(row, col + 17, product.standard_price, font_size_10)
            sheet.write(row, col + 18, product.list_price, font_size_10)
            sheet.write(row, col + 19, product.standard_price, font_size_10)

            row += 1

        r = 1
        testing.write('A1', 'Product Name', table_header_formate)
        testing.write('B1', 'Stock Move', table_header_formate)
        testing.write('C1', 'Account Move', table_header_formate)
        testing.set_column(0, 0, 30)
        testing.set_column(1, 1, 30)
        testing.set_column(2, 2, 30)
        testing.set_column(3, 3, 30)
        # stock_inventory = self.env['stock.inventory'].search([('id', '=', 7)])
        product_stock_move = self.env['stock.move'].search([])
        product_stocks = product_stock_move.mapped('product_id')
        for all_pr in all_product:
            c = 0
            if all_pr in product_stocks:
                testing.set_row(r, 30)
                stock_move = self.env['stock.move'].search([
                    ('product_id', '=', all_pr.id)
                ], limit=1)
                print('stock_move', stock_move.name)
                account_move_line = self.env['account.move.line'].search([
                    ('account_id.code', '=', '100700002'),
                    ('product_id', '=', all_pr.id),
                    ('date', '<=', self.date),
                ])
                testing.write(r, c, all_pr.name or '', font_size_10)
                c += 1
                testing.write(r, c, stock_move.name or '', font_size_10)
                c += 1
                if account_move_line:
                    for line in account_move_line:
                        testing.write(r, c, line.move_id.name or '', font_size_10)
                        c += 1
                else:
                    testing.write(r, c, '', font_size_10)
                    c += 1

                r += 1

        workbook.close()
        output.seek(0)

        self.write({'file_name': filename + str(self.date.strftime('%Y-%m-%d')) + '.xlsx'})
        self.excel_file = base64.b64encode(output.read())

        context = {
            'file_name': self.file_name,
            'excel_file': self.excel_file,
        }

        act_id = self.env['report.excel'].create(context)
        return act_id
