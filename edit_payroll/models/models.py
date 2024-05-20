# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import xlsxwriter
from io import BytesIO
import base64
from datetime import datetime


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_payslips_accrued = fields.Boolean()

    @api.constrains('is_payslips_accrued')
    def check_is_payslips_accrued(self):
        records = self.env['account.account'].search([('is_payslips_accrued', '=', True)])
        if len(records) > 1:
            raise ValidationError(
                _('Can not have multiple payslip accrued accounts: [%s, %s]' % (records[0].name, records[1].name)))


class HrContract(models.Model):
    _inherit = 'hr.contract'

    is_employer = fields.Boolean("Is Employer")


class HrPayslipRunReport(models.Model):
    _name = 'hr.payslip.run.report'

    name = fields.Char(required=True)
    datas = fields.Binary(required=True)
    payslip_run_id = fields.Many2one("hr.payslip.run")


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    report = fields.Binary(string='Download', readonly=True)
    report_name = fields.Char()
    payslip_run_reports = fields.One2many('hr.payslip.run.report', 'payslip_run_id')

    def board_member_report(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        font_size_10 = workbook.add_format(
            {'font_name': 'KacstBook', 'font_size': 10, 'align': 'center', 'valign': 'vcenter',  # 'text_wrap': True,
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

        sheet = workbook.add_worksheet('Board Member Report')
        sheet.set_column(0, 3, 40)
        sheet.set_row(0, 20)

        sheet.write('A1', 'Name', table_header_formate)
        sheet.write('B1', 'Title', table_header_formate)
        sheet.write('C1', 'Company Insurance', table_header_formate)
        sheet.write('D1', 'Social Insurance Start Date', table_header_formate)
        total = 0
        row = 1
        col = 0
        year = self.date_start.year
        record = self.env['board.member'].search([('name', '=', year)], limit=1)
        insurance_fixed_config = self.env['hr.insurance.year'].search([('year', '=', year)], order="year desc",
                                                                      limit=1)
        ratio = insurance_fixed_config and (insurance_fixed_config.employer_ratio / 100.0) or 0.21
        if record:
            for line in record.board_member_ids:
                sheet.write(row, col, line.name or '', font_size_10)
                sheet.write(row, col + 1, line.title or '', font_size_10)
                sheet.write(row, col + 3, str(line.social_insurance_s_date) or '', font_size_10)
                if insurance_fixed_config:
                    max_insurance_amount = insurance_fixed_config.insurance_amount_max
                    min_insurance_amount = insurance_fixed_config.insurance_amount_min
                    if min_insurance_amount <= line.amount <= max_insurance_amount:
                        amount = line.amount
                    elif line.amount < min_insurance_amount:
                        amount = min_insurance_amount
                    elif line.amount > max_insurance_amount:
                        amount = max_insurance_amount
                    else:
                        amount = line.amount
                    sheet.write(row, col + 2, str(amount * ratio) or '', font_size_10)
                    total += amount * ratio
                else:
                    sheet.write(row, col + 2, str(line.amount * ratio) or '', font_size_10)
                    total += line.amount * ratio
                row += 1
        sheet.write(row, col + 2, total or '', table_header_formate)
        workbook.close()
        output.seek(0)
        self.report = base64.b64encode(output.read())
        self.report_name = 'Board Member Report ' + str(datetime.today().strftime('%Y-%m-%d')) + '.xlsx'
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=hr.payslip.run&id=" + str(
                self.id) + "&filename=" + self.report_name + "&field=report&download=true",
            'target': 'self'
        }

    def _write_report(self, header, data, name):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(name)
        num_cols = len(data[0]) if data else 0
        font_size_10 = workbook.add_format(
            {'font_name': 'KacstBook', 'font_size': 10, 'align': 'center', 'valign': 'vcenter',  # 'text_wrap': True,
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

        # set width for the cells
        sheet.set_column(0, num_cols, 50)
        # set height of each cell
        for i in range(num_cols + 1):
            sheet.set_row(i, 20)

        for idx, head in enumerate(header):
            sheet.write(0, idx, head, table_header_formate)

        for row_idx, row in enumerate(data):
            for col_idx, col in enumerate(row):
                sheet.write(row_idx + 1, col_idx, col, font_size_10)

        if name == 'Loan report':
            paid_this_month = []
            for rec in data:
                paid_this_month.append(float(rec[3]))
            if data:
                sheet.write(int(row_idx) + 2, 3, str(sum(paid_this_month)), table_header_formate)

        workbook.close()
        output.seek(0)
        self.report = base64.b64encode(output.read())
        self.report_name = name + str(datetime.today().strftime('%Y-%m-%d')) + '.xlsx'
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=hr.payslip.run&id=" + str(
                self.id) + "&filename=" + self.report_name + "&field=report&download=true",
            'target': 'self'
        }

    def _fetch_suspended_employee_data(self):
        header = ['Name', 'Arabic Name', 'Functional Title', 'Character', 'HR Reference', 'Level', 'Attendance ID',
                  'Old ID', 'Assignment Number', 'Grade',
                  'Department', 'Job',
                  'Net']
        data = []

        def _set_value(val):
            return val if val else 'NULL'

        for payslip in self.slip_ids:
            if payslip.employee_id.state == 'suspended' or payslip.employee_id.state == 'terminated':
                if payslip.env['hr.suspended'].search(
                        [('employee_id', '=', payslip.employee_id.id), ('state', '=', 'approved'), '|',
                         ('date_to', '=', False), ('date_to', '>=', payslip.date_from)]):
                    row = []
                    row.append(_set_value(getattr(payslip.employee_id, 'name', 'NULL')))
                    row.append(_set_value(getattr(payslip.employee_id, 'arabic_name', 'NULL')))
                    func_id = getattr(payslip.employee_id, 'func_id', 'NULL')
                    row.append(func_id.name if func_id else 'NULL')
                    character_id = getattr(payslip.employee_id, 'character_id', 'NULL')
                    row.append(character_id.name if character_id else 'NULL')
                    title_id = getattr(payslip.employee_id, 'title_id', 'NULL')
                    row.append(title_id.name if title_id else 'NULL')
                    character_level_id = getattr(payslip.employee_id, 'character_level_id', 'NULL')
                    row.append(character_level_id.name if character_level_id else 'NULL')
                    row.append(_set_value(getattr(payslip.employee_id, 'attendance_id', 'NULL')))
                    row.append(_set_value(getattr(payslip.employee_id, 'old_id', 'NULL')))
                    row.append(_set_value(getattr(payslip.employee_id, 'assignment_number', 'NULL')))

                    grade = getattr(payslip.employee_id, 'grade', 'NULL')
                    row.append(grade.name if grade else 'NULL')

                    department = getattr(payslip.employee_id, 'department_id', 'NULL')
                    row.append(department.name if department else 'NULL')

                    job = getattr(payslip.employee_id, 'job_id', 'NULL')
                    row.append(job.name if job else 'NULL')

                    net = 0
                    for line in payslip.line_ids:
                        if line.code == 'NET':
                            net += line.total

                    row.append(net)

                    data.append(row)

        return header, data

    def suspended_report(self):
        header, data = self._fetch_suspended_employee_data()
        return self._write_report(header, data, name='Suspended report')
        # self.get_exist_or_regenerate("Suspended report")

    def _fetch_bank_report_data(self, not_cib=True):
        # get columns values to be writtn in excel report
        data = []
        sum = 0
        for payslip in self.slip_ids:
            row = {}
            # if employee has approved suspension records in batch start and end date, not add this employee
            if self.get_suspension_if_found(payslip.employee_id, self.date_start, self.date_end) != ' ':
                continue
            bank = payslip.employee_id.bank_id
            if not_cib and bank and bank.name.lower() != 'cib':
                sum += self.get_value_of_net_mins_cash(payslip.line_ids, payslip.employee_id.contract_id.cash_wage)
                row = {
                    'character': payslip.employee_id.character_id.name,
                    'hr_reference': payslip.employee_id.title_id.name,
                    'level': payslip.employee_id.character_level_id.name,
                    'employee_number': payslip.employee_id.attendance_id,
                    'full_name': payslip.employee_id.name,
                    'arabic_name': payslip.employee_id.arabic_name,
                    'branch_code': '',
                    'account_number': payslip.employee_id.bank_account_number,
                    'grade': payslip.employee_id.grade.name,
                    'account_type_code': '',
                    'customer_id': '',
                    'action_name': '',
                    'value': self.get_value_of_net_mins_cash(payslip.line_ids,
                                                             payslip.employee_id.contract_id.cash_wage),
                    'termination': self.get_termination_if_found(payslip.employee_id, self.date_start, self.date_end),
                }

                data.append(row)

            elif not not_cib and bank and bank.name.lower() == 'cib':
                sum += self.get_value_of_net_mins_cash(payslip.line_ids, payslip.employee_id.contract_id.cash_wage)
                row = {
                    'character': payslip.employee_id.character_id.name,
                    'hr_reference': payslip.employee_id.title_id.name,
                    'level': payslip.employee_id.character_level_id.name,
                    'employee_number': payslip.employee_id.attendance_id,
                    'full_name': payslip.employee_id.name,
                    'arabic_name': payslip.employee_id.arabic_name,
                    'branch_code': '',
                    'account_number': payslip.employee_id.bank_account_number,
                    'grade': payslip.employee_id.grade.name,
                    'account_type_code': '',
                    'customer_id': '',
                    'action_name': '',
                    'value': self.get_value_of_net_mins_cash(payslip.line_ids,
                                                             payslip.employee_id.contract_id.cash_wage),
                    'termination': self.get_termination_if_found(payslip.employee_id, self.date_start, self.date_end),
                }

                data.append(row)

        last_row = {
            'character': 'TOTAL',
            'hr_reference': '',
            'level': '',
            'employee_number': '',
            'full_name': '',
            'arabic_name': '',
            'branch_code': '',
            'account_number': '',
            'grade': '',
            'account_type_code': '',
            'customer_id': '',
            'action_name': '',
            'value': sum,
            'termination': ''
        }
        data.append(last_row)

        return data

    def _write_bank_data_to_excel_file(self, data, bank_name='Egy Bank'):
        # data is [{data key,value},{}]
        # num of rows
        num_rows = len(data)
        num_cols = len(data[0]) if data else 0

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Bank Sheet')
        font_size_10 = workbook.add_format(
            {'font_name': 'KacstBook', 'font_size': 10, 'align': 'center', 'valign': 'vcenter',  # 'text_wrap': True,
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

        # set width for the cells
        sheet.set_column(0, num_cols, 50)
        # set height of each cell
        for i in range(num_cols + 1):
            sheet.set_row(i, 20)

        # writing data to the file
        # fist write the headers or columns' names
        # write first row as static data as requested
        sheet.write('A2', 'Payroll Name:MobiServe Egypt Monthly Payroll', table_header_formate)
        sheet.write('B2', 'Org Payment Method Name:Bank Transfer EG', table_header_formate)
        sheet.write('C2', 'Bank Name:%s' % bank_name, table_header_formate)

        col_headers = ['Character', 'HR Reference', 'Level', 'Employee Number', 'Full Name', 'Arabic Name',
                       'Branch Code', 'Account Number',
                       'Grade',
                       'Account Type Code', 'Customer Id', 'Action Name', 'Value', 'Termination']
        row = 3
        col = 0
        counter = 0
        for col_header in col_headers:
            sheet.write(row, col + counter, col_header or '', font_size_10)
            counter = counter + 1

        # second writing the data
        row = 4
        for rec in data:
            sheet.write(row, 0, rec['character'] or '', font_size_10)
            sheet.write(row, 1, rec['hr_reference'] or '', font_size_10)
            sheet.write(row, 2, rec['level'] or '', font_size_10)
            sheet.write(row, 3, rec['employee_number'] or '', font_size_10)
            sheet.write(row, 4, rec['full_name'] or '', font_size_10)
            sheet.write(row, 5, rec['arabic_name'] or '', font_size_10)
            sheet.write(row, 6, rec['branch_code'] or '', font_size_10)
            sheet.write(row, 7, rec['account_number'] or '', font_size_10)
            sheet.write(row, 8, rec['grade'] or '', font_size_10)
            sheet.write(row, 9, rec['account_type_code'] or '', font_size_10)
            sheet.write(row, 10, rec['customer_id'] or '', font_size_10)
            sheet.write(row, 11, rec['action_name'] or '', font_size_10)
            sheet.write(row, 12, rec['value'] or '', font_size_10)
            sheet.write(row, 13, rec['termination'] or '', font_size_10)

            row = row + 1

        # end of writing, close file
        workbook.close()
        output.seek(0)
        self.report = base64.b64encode(output.read())
        self.report_name = "Bank Sheet" + str(datetime.today().strftime('%Y-%m-%d')) + '.xlsx'
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=hr.payslip.run&id=" + str(
                self.id) + "&filename=" + self.report_name + "&field=report&download=true",
            'target': 'self'
        }

    def bank_cib_report(self):
        data = self._fetch_bank_report_data(not_cib=False)
        return self._write_bank_data_to_excel_file(data, bank_name='CIB')

    # def board_member_moves(self, res):
    #     year = self.date_start.year
    #     record = self.env['board.member'].search([('name', '=', year)], limit=1)
    #     insurance_fixed_config = self.env['hr.insurance.year'].search([('year', '=', year)], order="year desc",
    #                                                                   limit=1)
    #     ratio = insurance_fixed_config and (insurance_fixed_config.employer_ratio / 100.0) or 0.21
    #     if record:
    #         moves = {}
    #         for line in record.board_member_ids:
    #             if insurance_fixed_config:
    #                 max_insurance_amount = insurance_fixed_config.insurance_amount_max
    #                 min_insurance_amount = insurance_fixed_config.insurance_amount_min
    #                 if min_insurance_amount <= line.amount <= max_insurance_amount:
    #                     amount = line.amount
    #                 elif line.amount < min_insurance_amount:
    #                     amount = min_insurance_amount
    #                 elif line.amount > max_insurance_amount:
    #                     amount = max_insurance_amount
    #                 else:
    #                     amount = line.amount
    #                 result = amount * ratio
    #             else:
    #                 result = line.amount * ratio
    #             salary_rule = self.env.ref('centione_insurance.company_insurance_subscription_alw')
    #             if salary_rule:
    #                 is_debit = salary_rule.debit_or_credit == 'debit'
    #                 if line.opex_cogs == 'opex':
    #                     account = salary_rule.opex
    #                 elif line.opex_cogs == 'cogs':
    #                     account = salary_rule.cogs
    #                 else:
    #                     account = salary_rule.opex
    #                 key = str(account.id)
    #
    #                 if salary_rule.is_considered:
    #                     if key in moves:
    #                         moves[key][0 if is_debit else 1] += abs(result)
    #                     else:
    #                         val = [0, 0]
    #                         moves.update({key: val})
    #                         moves[key][0 if is_debit else 1] += abs(result)
    #         sum_credit = sum_debit = 0
    #         for key in moves:
    #             diff = moves[key][0] - moves[key][1]
    #             moves[key] = [abs(diff), 0] if diff > 0 else [0, abs(diff)]
    #             sum_debit += moves[key][0]
    #             sum_credit += moves[key][1]
    #
    #         accrued_account = self.env['account.account'].search([('is_payslips_accrued', '=', True)])
    #         if len(accrued_account) == 0:
    #             raise ValidationError(_('Accrued Account is not set'))
    #
    #         accrued_account_id = str(accrued_account[0].id)
    #
    #         if sum_credit > sum_debit:
    #             moves[accrued_account_id] = [abs(sum_credit - sum_debit), 0]
    #         elif sum_credit < sum_debit:
    #             moves[accrued_account_id] = [0, abs(sum_credit - sum_debit)]
    #
    #         account_move_lines = []
    #         for key in moves:
    #             decoded_key = key.split('_')
    #             account_id = int(decoded_key[0]) if decoded_key[0].isnumeric() else False
    #             analytic_account_id = False
    #             analytic_tag_id = False
    #             if len(decoded_key) == 3:
    #                 analytic_account_id = int(decoded_key[1]) if decoded_key[1].isnumeric() else False
    #                 analytic_tag_id = int(decoded_key[2]) if decoded_key[2].isnumeric() else False
    #
    #             if account_id:
    #                 move_line = (0, 0, {
    #                     'account_id': account_id,
    #                     'analytic_distribution': {analytic_account_id: 100},
    #                     'analytic_tag_ids': [[6, 0, [analytic_tag_id] if analytic_tag_id else []]],
    #                     'debit': moves[key][0],
    #                     'credit': moves[key][1],
    #                 })
    #                 account_move_lines.append(move_line)
    #         res.sudo().write({
    #             'line_ids': account_move_lines
    #         })
    #
    # def close_payslip_run(self, *args, **kwargs):
    #     res = super(HrPayslipRun, self).close_payslip_run(*args, **kwargs)
    #     self.board_member_moves(res)
    #     return res
