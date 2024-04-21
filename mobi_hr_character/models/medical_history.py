import base64
import datetime
from io import BytesIO
import xlsxwriter
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrGrade(models.Model):
    _name = 'hr.grade'
    _description = "HrGrade"

    name = fields.Char()


class HrMedicalInsuranceLines(models.Model):
    _name = 'hr.medical.insurance.lines'
    _description = "HrMedicalInsuranceLines"

    medical_id = fields.Many2one('hr.medical.insurance')
    grade_id = fields.Many2one('hr.grade')
    name = fields.Char(related='grade_id.name', store=True)
    subscription = fields.Float()
    company_share = fields.Float()
    company_share_percentage = fields.Boolean()
    employee_share = fields.Float()
    employee_share_percentage = fields.Boolean()
    fees = fields.Float()
    fees_percentage = fields.Boolean()
    tax = fields.Float()
    tax_percentage = fields.Boolean()
    total_employee_share = fields.Float(compute='_compute_total_employee_share', store=True)

    @api.depends('employee_share', 'employee_share_percentage',
                 'fees', 'fees_percentage',
                 'tax', 'tax_percentage',
                 'subscription')
    def _compute_total_employee_share(self):
        for rec in self:
            employee_share = (
                                     rec.employee_share / 100) * rec.subscription if rec.employee_share_percentage else rec.employee_share
            fees = (rec.fees / 100) * rec.subscription if rec.fees_percentage else rec.fees
            tax = (rec.tax / 100) * rec.subscription if rec.tax_percentage else rec.tax
            rec.total_employee_share = employee_share + fees + tax

    def get_company_share(self):
        for rec in self:
            if not rec.company_share_percentage:
                return rec.company_share

            return (rec.company_share / 100.0) * rec.subscription


class HrMedicalLines(models.Model):
    _name = 'medical.grade.family'

    grade_id = fields.Many2one('hr.grade', string='Grade', required=1)
    medical_id = fields.Many2one('hr.medical.insurance', string='Medical Insurance')
    spouse = fields.Float('Spouse')
    child = fields.Float('Child')
    on_company = fields.Boolean()
    company_percentage = fields.Float(string="Company Percentage")
    employee_percentage = fields.Float(string="Employee Percentage")

    @api.constrains('company_percentage', 'employee_percentage')
    def check(self):
        for rec in self:
            if rec.company_percentage + rec.employee_percentage > 100:
                raise ValidationError("Percentage Must Be Less Than !00%")


class HrMedicalInsurance(models.Model):
    _name = 'hr.medical.insurance'
    _description = "HrMedicalInsurance"

    name = fields.Char()
    insurance_company_id = fields.Many2one('hr.insurance.company')
    max_allowed_grades = fields.Integer()
    line_ids = fields.One2many('hr.medical.insurance.lines', 'medical_id')
    max_number_subscribers = fields.Integer()
    number_of_subscribers = fields.Integer(compute='_compute_number_of_subscribers', store=True)
    subscribers_ids = fields.One2many('hr.employee.medical.line', 'medical_id')
    date_from = fields.Date()
    date_to = fields.Date()
    critical_case_allowance = fields.Float()
    state = fields.Selection([('draft', 'Draft'), ('open', 'Running'),
                              ('close', 'Expired'), ('cancel', 'Cancelled')], default='draft')
    report = fields.Binary(string='Download', readonly=True)
    report_name = fields.Char()
    family_grade_ids = fields.One2many('medical.grade.family', 'medical_id', string='Family Grade')

    def generate_xlsx_report(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Medical Insurance Sheet')
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
        table_header_formate = workbook.add_format({
            'bold': 1,
            'border': 1,
            'bg_color': '#a4aba6',
            'font_size': '10',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        sheet.set_column(0, 0, 10, without_borders)
        sheet.set_column(1, 1, 40, without_borders)
        sheet.set_column(2, 35, 30, without_borders)
        sheet.write('A1', 'Character', table_header_formate)
        sheet.write('B1', 'Oracle ID', table_header_formate)
        sheet.write('C1', 'Employee Name', table_header_formate)
        sheet.write('D1', 'Date Of Birth', table_header_formate)
        sheet.write('E1', 'Company Name', table_header_formate)
        sheet.write('F1', 'Hire Date', table_header_formate)
        sheet.write('G1', 'Medical Grade ', table_header_formate)
        sheet.write('H1', 'Salary Grade', table_header_formate)
        sheet.write('I1', 'Job', table_header_formate)
        sheet.write('J1', 'Position', table_header_formate)
        sheet.write('K1', 'Organization', table_header_formate)
        sheet.write('L1', 'Location', table_header_formate)
        sheet.write('M1', 'Wife Name ', table_header_formate)
        sheet.write('N1', 'Date of birth', table_header_formate)
        sheet.write('O1', 'start date', table_header_formate)
        sheet.write('P1', 'End Data', table_header_formate)
        sheet.write('Q1', 'First Child', table_header_formate)
        sheet.write('R1', 'Date Of Birth 1', table_header_formate)
        sheet.write('S1', 'First Child Start Date', table_header_formate)
        sheet.write('T1', 'First Child End Date', table_header_formate)
        sheet.write('U1', 'Second Child', table_header_formate)
        sheet.write('V1', 'Date Of Birth 2', table_header_formate)
        sheet.write('W1', 'Second Child Start Date', table_header_formate)
        sheet.write('X1', 'Second Child End Date', table_header_formate)
        sheet.write('Y1', 'Third Child', table_header_formate)
        sheet.write('Z1', 'Date Of Birth 3', table_header_formate)
        sheet.write('AA1', 'Third Child Start Date', table_header_formate)
        sheet.write('AB1', 'Third Child end Date', table_header_formate)
        sheet.write('AC1', 'Fourth Child', table_header_formate)
        sheet.write('AD1', 'Date Of Birth 4', table_header_formate)
        sheet.write('AE1', 'Fourth Child Start Date', table_header_formate)
        sheet.write('AF1', 'Fourth Child end date', table_header_formate)
        sheet.write('AG1', 'Assignment Status', table_header_formate)
        sheet.write('AH1', 'Company Share', table_header_formate)
        sheet.write('AI1', 'Employee Share Total', table_header_formate)
        sheet.write('AJ1', 'Total', table_header_formate)
        row = 1
        col = 0
        for subscriber in self.subscribers_ids:
            if subscriber.employee_id.state == 'active':
                grade = self.env['medical.grade.family'].sudo().search(
                    [('grade_id', '=', subscriber.medical_grade_id.grade_id.id), ('medical_id', '=', self.id)], limit=1)
                employee_spouse = 0
                employee_child = 0
                sheet.write(row, col + 0, str(subscriber.sudo().employee_id.character_id.name) or '', font_size_10)
                sheet.write(row, col + 1, str(subscriber.sudo().employee_id.attendance_id) or '', font_size_10)
                sheet.write(row, col + 2, str(subscriber.sudo().employee_id.name) or '', font_size_10)
                sheet.write(row, col + 3, str(subscriber.sudo().employee_id.birthday) or '', font_size_10)
                sheet.write(row, col + 4, str(subscriber.sudo().employee_id.company_id.name) or '', font_size_10)
                sheet.write(row, col + 5, str(subscriber.sudo().employee_id.hire_date) or '', font_size_10)
                sheet.write(row, col + 6, str(subscriber.sudo().medical_grade_id.name) or '', font_size_10)
                sheet.write(row, col + 7, str(subscriber.sudo().employee_id.grade.name) or '', font_size_10)
                sheet.write(row, col + 8, str(subscriber.sudo().employee_id.job) or '', font_size_10)
                sheet.write(row, col + 9, str(subscriber.sudo().employee_id.job_id.name) or '', font_size_10)
                sheet.write(row, col + 10, str(subscriber.sudo().employee_id.organisation.name) or '', font_size_10)
                sheet.write(row, col + 11, str(subscriber.sudo().employee_id.work_location) or '', font_size_10)
                for record in subscriber.sudo().follower_ids:
                    if record.relative_relation == 'spouse':
                        if grade:
                            employee_spouse += grade.spouse
                        sheet.write(row, col + 12, str(record.name) or '', font_size_10)
                        sheet.write(row, col + 13, str(record.birth_date) or '', font_size_10)
                        sheet.write(row, col + 14, str(self.date_from) or '', font_size_10)
                        sheet.write(row, col + 15, str(self.date_to) or '', font_size_10)
                n = 1
                column = col + 16
                for record in subscriber.sudo().follower_ids:
                    if record.relative_relation == 'child' and n < 5:
                        if grade:
                            employee_child += grade.child
                        sheet.write(row, column, str(record.name) or '', font_size_10)
                        sheet.write(row, column + 1, str(record.birth_date) or '', font_size_10)
                        sheet.write(row, column + 2, str(self.date_from) or '', font_size_10)
                        sheet.write(row, column + 3, str(self.date_to) or '', font_size_10)
                        n += 1
                        column += 4
                sheet.write(row, col + 32,
                            str('Active Assignment' if subscriber.sudo().employee_id.active else '') or '',
                            font_size_10)
                sheet.write(row, col + 33, str(
                    subscriber.sudo().medical_grade_id.company_share + (
                            employee_child + employee_spouse) * grade.company_percentage / 100) or '',
                            font_size_10)
                sheet.write(row, col + 34, str(subscriber.sudo().medical_grade_id.total_employee_share + (
                        employee_child + employee_spouse) * grade.employee_percentage / 100) or '',
                            font_size_10)
                sheet.write(row, col + 35, str(
                    subscriber.sudo().medical_grade_id.company_share + subscriber.sudo().medical_grade_id.total_employee_share + (
                            (employee_child + employee_spouse) * grade.company_percentage / 100) + (
                            (employee_child + employee_spouse) * grade.employee_percentage / 100)) or '',
                            font_size_10)
                row += 1
        workbook.close()
        output.seek(0)
        self.write({'report': base64.encodestring(output.getvalue())})
        return {
            'type': 'ir.actions.act_url',
            'name': 'Orders Sheet',
            'url': '/web/content/hr.medical.insurance/%s/report/MedicalInsurance Sheet.xlsx?download=true' % (
                self.id),
            'target': 'new'
        }

    @api.constrains('line_ids')
    def _check_max_grades(self):
        for rec in self:
            if len(rec.line_ids) > rec.max_allowed_grades:
                raise ValidationError("Exceeded Max allowed grades!!")

    @api.depends('subscribers_ids')
    def _compute_number_of_subscribers(self):
        for rec in self:
            rec.number_of_subscribers = len(rec.subscribers_ids) + sum([len(sub.follower_ids)
                                                                        for sub in
                                                                        [sub for sub in rec.subscribers_ids]])
            if rec.number_of_subscribers > rec.max_number_subscribers:
                raise ValidationError("Exceeded Max allowed subscribers for this Medical Contract")

    def subscribers_report(self):
        for rec in self:
            header, data = rec._fetch_data()
            rec._write_report(header, data, 'Medical Care report')

    def _fetch_data(self):
        header = ['Attendance ID', 'Name', 'Medical Grade', 'Company Share', 'Company Share percentage?',
                  'Employee Share', 'Employee Share percentage?', 'Cost', 'Followers']
        for rec in self:
            data = []
            for subscriber in rec.subscribers_ids:
                row = []

                attendance_id = getattr(subscriber.employee_id, 'attendance_id', 'NULL')
                row.append(attendance_id if attendance_id else 'NULL')

                name = getattr(subscriber.employee_id, 'name', 'NULL')
                row.append(name if name else name)

                row.append(subscriber.medical_grade_id.name)
                row.append(subscriber.medical_grade_id.company_share)

                company_share_percentage = subscriber.medical_grade_id.company_share_percentage
                row.append('Yes' if company_share_percentage else 'No')

                row.append(subscriber.medical_grade_id.total_employee_share)

                employee_share_percentage = subscriber.medical_grade_id.employee_share_percentage
                row.append('Yes' if employee_share_percentage else 'No')

                row.append(subscriber.cost / 12.0)
                row.append(len(subscriber.follower_ids))

                data.append(row)

        return header, data

    def _write_report(self, header, data, name):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(name)

        for idx, head in enumerate(header):
            sheet.write(0, idx, head)

        for row_idx, row in enumerate(data):
            for col_idx, col in enumerate(row):
                sheet.write(row_idx + 1, col_idx, col)

        workbook.close()
        output.seek(0)
        self.report = base64.encodestring(output.read())
        self.report_name = name + str(datetime.today().strftime('%Y-%m-%d')) + '.xlsx'


class HrEmployeeMedicalLine(models.Model):
    _name = 'hr.employee.medical.line'
    _description = "HrEmployeeMedicalLine"

    employee_id = fields.Many2one('hr.employee')
    medical_id = fields.Many2one('hr.medical.insurance', domain=[('state', '=', 'open')])
    medical_grade_id = fields.Many2one('hr.medical.insurance.lines', domain=[('medical_id', '=', False)])
    date_from = fields.Date(related='medical_id.date_from')
    date_to = fields.Date(related='medical_id.date_to')
    follower_ids = fields.Many2many('hr.employee.follower', domain="[('employee_id', '=', employee_id)]")
    cost = fields.Float(compute='_compute_cost')

    @api.constrains('medical_id', 'medical_grade_id', 'date_from', 'date_to', 'follower_ids', 'cost', 'employee_id')
    def check_history_fields(self, date=datetime.date.today()):
        for rec in self:
            if rec.employee_id:
                rec.env['hr.employee.medical.history'].create(
                    {'date': date, 'employee_id': rec.employee_id.id, 'medical_id': rec.medical_id.id,
                     'medical_grade_id': rec.medical_grade_id.id, 'date_from': rec.date_from, 'date_to': rec.date_to,
                     'follower_ids': [(6, 0, rec.follower_ids.ids)], 'cost': rec.cost})

    @api.onchange('medical_id')
    def _onchange_medical_id(self):
        domain = {'medical_grade_id': [('medical_id', '=', -1)]}
        for rec in self:
            if rec.medical_id:
                domain = {'medical_grade_id': [('id', 'in', [line.id for line in rec.medical_id.line_ids])]}
                rec.medical_grade_id = False
        return {'domain': domain}

    @api.constrains('follower_ids')
    def _update_number_subscribers(self):
        for rec in self:
            rec.medical_id._compute_number_of_subscribers()

    @api.depends('medical_grade_id', 'follower_ids')
    def _compute_cost(self):
        for rec in self:
            employee_cost = rec.medical_grade_id.total_employee_share
            comapany_share = rec.medical_grade_id.get_company_share()
            if comapany_share:
                rec.cost = employee_cost + (employee_cost + comapany_share) * len(rec.follower_ids)
            else:
                rec.cost = rec.cost


class HrEmployeeMedicalHistory(models.Model):
    _name = 'hr.employee.medical.history'
    _description = "HrEmployeeMedicalHistory"

    employee_id = fields.Many2one('hr.employee')
    medical_id = fields.Many2one('hr.medical.insurance', domain=[('state', '=', 'open')])
    medical_grade_id = fields.Many2one('hr.medical.insurance.lines', domain=[('medical_id', '=', False)])
    date_from = fields.Date()
    date_to = fields.Date()
    follower_ids = fields.Many2many('hr.employee.follower', domain="[('employee_id', '=', employee_id)]")
    cost = fields.Float()
    date = fields.Date()


class HrEmployeeFollower(models.Model):
    _name = 'hr.employee.follower'
    _description = "HrEmployeeFollower"

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee')
    birth_date = fields.Date()


class HrEmployeeLifeLine(models.Model):
    _name = 'hr.employee.life.line'
    _description = "HrEmployeeLifeLine"

    employee_id = fields.Many2one('hr.employee')
    life_id = fields.Many2one('hr.life.insurance', domain=[('state', '=', 'open')])
    life_grade_id = fields.Many2one('hr.life.insurance.lines', domain=[('life_id', '=', False)])
    date_from = fields.Date(related='life_id.date_from')
    date_to = fields.Date(related='life_id.date_to')
    follower_ids = fields.Many2many('hr.employee.follower', domain="[('employee_id', '=', employee_id)]")
    cost = fields.Float(compute='_compute_cost')

    @api.constrains('life_id', 'life_grade_id', 'date_from', 'date_to', 'follower_ids', 'cost', 'employee_id')
    def check_history_fields(self, date=datetime.date.today()):
        for rec in self:
            if rec.employee_id:
                rec.env['hr.employee.life.history'].create(
                    {'date': date, 'employee_id': rec.employee_id.id, 'life_id': rec.life_id.id,
                     'life_grade_id': rec.life_grade_id.id, 'date_from': rec.date_from, 'date_to': rec.date_to,
                     'follower_ids': [(6, 0, rec.follower_ids.ids)], 'cost': rec.cost})

    @api.onchange('life_id')
    def _onchange_life_id(self):
        domain = {'life_grade_id': [('life_id', '=', -1)]}
        for rec in self:
            if rec.life_id:
                domain = {'life_grade_id': [('id', 'in', [line.id for line in rec.life_id.line_ids])]}
                rec.life_grade_id = False
        return {'domain': domain}

    @api.depends('life_grade_id', 'follower_ids')
    def _compute_cost(self):
        for rec in self:
            employee_cost = rec.life_grade_id.total_employee_share
            rec.cost = employee_cost + employee_cost * len(rec.follower_ids)


class HrLifeInsuranceLines(models.Model):
    _name = 'hr.life.insurance.lines'
    _description = "HrLifeInsuranceLines"

    life_id = fields.Many2one('hr.life.insurance')
    grade_id = fields.Many2one('hr.grade')
    name = fields.Char(related='grade_id.name', store=True)
    subscription = fields.Float()
    company_share = fields.Float()
    company_share_percentage = fields.Boolean()
    employee_share = fields.Float()
    employee_share_percentage = fields.Boolean()
    fees = fields.Float()
    fees_percentage = fields.Boolean()
    tax = fields.Float()
    tax_percentage = fields.Boolean()
    total_employee_share = fields.Float(compute='_compute_total_employee_share', store=True)

    @api.depends('employee_share', 'employee_share_percentage',
                 'fees', 'fees_percentage',
                 'tax', 'tax_percentage',
                 'subscription')
    def _compute_total_employee_share(self):
        for rec in self:
            employee_share = (
                                     rec.employee_share / 100) * rec.subscription if rec.employee_share_percentage else rec.employee_share
            fees = (rec.fees / 100) * rec.subscription if rec.fees_percentage else rec.fees
            tax = (rec.tax / 100) * rec.subscription if rec.tax_percentage else rec.tax
            rec.total_employee_share = employee_share + fees + tax


class HrLifeInsurance(models.Model):
    _name = 'hr.life.insurance'
    _description = "HrLifeInsurance"

    name = fields.Char()
    insurance_company_id = fields.Many2one('hr.insurance.company')
    line_ids = fields.One2many('hr.life.insurance.lines', 'life_id')
    date_from = fields.Date()
    date_to = fields.Date()
    subscribers_ids = fields.One2many('hr.employee.life.line', 'life_id')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Running'),
                              ('close', 'Expired'), ('cancel', 'Cancelled')], default='draft')

    report = fields.Binary(string='Download', readonly=True)
    report_name = fields.Char()

    def subscribers_report(self):
        for rec in self:
            header, data = rec._fetch_data()
            rec._write_report(header, data, 'Life insurance report')

    def _fetch_data(self):
        header = ['Attendance ID', 'Name', 'Medical Grade', 'Company Share', 'Company Share percentage?',
                  'Employee Share', 'Employee Share percentage?', 'Cost']
        for rec in self:
            data = []
            for subscriber in rec.subscribers_ids:
                row = []

                attendance_id = getattr(subscriber.employee_id, 'attendance_id', 'NULL')
                row.append(attendance_id if attendance_id else 'NULL')

                name = getattr(subscriber.employee_id, 'name', 'NULL')
                row.append(name if name else name)

                row.append(subscriber.life_grade_id.name)
                row.append(subscriber.life_grade_id.company_share)

                company_share_percentage = subscriber.life_grade_id.company_share_percentage
                row.append('Yes' if company_share_percentage else 'No')

                row.append(subscriber.life_grade_id.total_employee_share)

                employee_share_percentage = subscriber.life_grade_id.employee_share_percentage
                row.append('Yes' if employee_share_percentage else 'No')

                row.append(subscriber.cost / 12.0)

                data.append(row)

            return header, data

    def _write_report(self, header, data, name):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(name)

        for idx, head in enumerate(header):
            sheet.write(0, idx, head)

        for row_idx, row in enumerate(data):
            for col_idx, col in enumerate(row):
                sheet.write(row_idx + 1, col_idx, col)

        workbook.close()
        output.seek(0)
        self.report = base64.encodestring(output.read())
        self.report_name = name + str(datetime.today().strftime('%Y-%m-%d')) + '.xlsx'


class HrInsuranceCompany(models.Model):
    _name = 'hr.insurance.company'
    _description = "HrInsuranceCompany"

    name = fields.Char()


class HrEmployeeLifeHistory(models.Model):
    _name = 'hr.employee.life.history'
    _description = "HrEmployeeLifeHistory"

    employee_id = fields.Many2one('hr.employee')
    life_id = fields.Many2one('hr.life.insurance', domain=[('state', '=', 'open')])
    life_grade_id = fields.Many2one('hr.life.insurance.lines', domain=[('life_id', '=', False)])
    date_from = fields.Date()
    date_to = fields.Date()
    follower_ids = fields.Many2many('hr.employee.follower', domain="[('employee_id', '=', employee_id)]")
    cost = fields.Float()
    date = fields.Date()
