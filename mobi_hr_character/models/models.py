# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.osv import expression
import datetime


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account', check_company=True, related="employee_id.cost_center_id",
        store=True, readonly=False)


class HrCluster(models.Model):
    _name = 'hr.cluster'

    name = fields.Char(required=True)
    character_ids = fields.One2many('hr.character', 'cluster_id')


class HrCharacter(models.Model):
    _name = 'hr.character'

    name = fields.Char(required=True)
    title_ids = fields.One2many('hr.title', 'character_id')
    cluster_id = fields.Many2one('hr.cluster')


class HrTitle(models.Model):
    _name = 'hr.title'

    name = fields.Char(required=True)
    character_id = fields.Many2one('hr.character')
    character_level_ids = fields.One2many('hr.character.level', 'title_id')


class HrCharacter_level(models.Model):
    _name = 'hr.character.level'

    name = fields.Char(required=True)
    title_id = fields.Many2one('hr.title')


class FuncTitle(models.Model):
    _name = 'func.title'

    name = fields.Char(required=True)


class EmployeeCategory(models.Model):
    _name = 'employee.category'

    name = fields.Char(required=True)


class PaymentMethodEmployee(models.Model):
    _name = 'payment.method.employee'

    name = fields.Char(required=True)


class PeopleGroup(models.Model):
    _name = 'people.group'

    name = fields.Char(required=True)


class EmployeeGrade(models.Model):
    _name = 'employee.grade'

    name = fields.Char(required=True)


class EmployeeOrganisation(models.Model):
    _name = 'employee.organisation'

    name = fields.Char(required=True)


class EmployeeDivision(models.Model):
    _name = 'employee.division'

    name = fields.Char(required=True)


class MilitaryStatus(models.Model):
    _name = 'military.status'

    name = fields.Char(required=True)


class ResBankCustom(models.Model):
    _name = 'res.bank.custom'

    name = fields.Char(required=True)


class ResPartnerBankCustom(models.Model):
    _name = 'res.partner.bank.custom'

    name = fields.Char(required=True)


class HrDepartmentInherit(models.Model):
    _inherit = 'hr.department'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', tracking=True)
    opex_cogs = fields.Selection([('opex', 'Opex'), ('cogs', 'Cogs')], tracking=True)


class HrJobInherit(models.Model):
    _inherit = 'hr.job'

    jop = fields.Char(string="Jop")


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    jop = fields.Char(string="Jop", related="job_id.jop")
    payment_method = fields.Char()
    payment_method_id = fields.Many2one(comodel_name="payment.method.employee", string="Payment Method")
    travel_to = fields.Char(string="Travel To")
    embassy_name = fields.Char(string="Embassy Name")
    func_id = fields.Many2one('func.title', string="Functional Title")
    cluster_id = fields.Many2one('hr.cluster', string="Cluster")
    character_id = fields.Many2one('hr.character', string="Character")
    title_id = fields.Many2one('hr.title', string="Hr Reference")
    character_level_id = fields.Many2one('hr.character.level', string="Level")
    military_status_id = fields.Many2one('military.status', string="Military Status")
    military_status = fields.Char(string="Military Status")
    military_start_date = fields.Date()
    military_end_date = fields.Date()
    military_card_number = fields.Char(string="Military Card Number")
    person_type = fields.Char(string="Person Type")
    employee_arabic = fields.Char(tracking=True)
    is_a_handicap = fields.Boolean(copy=False, tracking=True)
    employee_attendance_id = fields.Char(string="Employee Attendance ID", tracking=True, copy=False, default="NEW")
    tow_annual = fields.Boolean(copy=False, tracking=True)
    arabic_department = fields.Char(copy=False, tracking=True)
    arabic_job_position = fields.Char(copy=False, tracking=True)
    full_name = fields.Char()
    bank_id = fields.Many2one(comodel_name="res.bank.custom")
    bank_account_number_id = fields.Many2one(comodel_name="res.partner.bank.custom")
    # Private Information
    private_address = fields.Char()
    old_id = fields.Char(string="Old ID")
    social_insurance_no = fields.Char()
    social_insurance_office = fields.Char()
    insurance_start_date = fields.Datetime()
    insurance_end_date = fields.Datetime()
    basic_insurance_salary = fields.Float()
    for_vacation_balance = fields.Integer(string="Social Insurance Date For Vacation Balance")
    no_create_allocation_leaves = fields.Boolean()
    employee_category_id = fields.Many2one(comodel_name="employee.category")
    military_description = fields.Char()
    spouse = fields.Char()
    spouse_complete_name = fields.Char()
    spouse_birthdate_employee = fields.Datetime(string="Spouse Birthdate")
    retirement_date = fields.Date(string="Retirement Date", compute='_compute_pension_date', store=True)
    region = fields.Char(string="Religion")
    people_group_id = fields.Many2one(comodel_name="people.group")
    grade_id = fields.Many2one(comodel_name="employee.grade")
    hire_date = fields.Datetime()
    organisation_id = fields.Many2one(comodel_name="employee.organisation")
    assignment_number = fields.Char()
    project_id = fields.Many2one(comodel_name="project.project")
    sub_project = fields.Char()
    cost_center_id = fields.Many2one(comodel_name="account.analytic.account")
    account_analytic_Tag_id = fields.Many2one(comodel_name="account.analytic.tag")
    first_hire_date = fields.Datetime()
    division_id = fields.Many2one(comodel_name="employee.division")
    opex_cogs = fields.Selection(related='department_id.opex_cogs')
    employee_documents = fields.Char()
    additional_note = fields.Text()
    home_phone = fields.Char()
    # HR Settings
    automatic_absence = fields.Boolean(copy=False)
    transfer_all_allocation = fields.Boolean(copy=False)
    total_loan_unpaid = fields.Float()
    remaining_legal_leaves = fields.Float()
    medical_exam = fields.Datetime()
    company_vehicle = fields.Char()
    # page Medical Care
    life_insurance = fields.Boolean()
    life_insurance_date = fields.Date()
    medical_insurance = fields.Boolean()
    medical_insurance_date = fields.Date()
    max_insurance_limit_type = fields.Selection([('value', 'Value'), ('percentage', 'Percentage')], default='value')
    max_insurance_limit_value = fields.Float()
    max_insurance_limit_percentage = fields.Float()
    rate_type = fields.Selection([('value', 'Value'), ('percentage', 'Percentage')], default='value')
    rate_value = fields.Float()
    rate_percentage = fields.Float()
    preposition_ids = fields.One2many('hr.preposition', 'employee_id')
    medical_care_ids = fields.One2many("hr.medical.care", 'employee_id')
    # Medical History
    medical_history_ids = fields.One2many('hr.employee.medical.history', 'employee_id')
    # penalty
    penalty_ids = fields.One2many('hr.penalty', 'penalty_id')
    # document
    document_ids = fields.One2many('hr.document', 'employee_id')
    # Excuses
    number_excuse_month = fields.Integer(string="Number Of Total Excuses In Month", default=2.0, required=False, )
    period_excuse_month = fields.Float(string="Period of Total Excuses In Month", default=6.00, required=False, )
    period_one_excuse = fields.Float(string="Period of One Excuse", default=3.00, required=False, )
    # medical_line
    medical_line_ids = fields.One2many('hr.employee.medical.line', 'employee_id')
    # life_line
    life_line_ids = fields.One2many('hr.employee.life.line', 'employee_id')
    # follower
    follower_ids = fields.One2many('hr.employee.follower', 'employee_id')
    # life_history
    life_history_ids = fields.One2many('hr.employee.life.history', 'employee_id')

    @api.depends('birthday')
    def _compute_pension_date(self):
        for rec in self:
            if rec.birthday:
                rec.retirement_date = rec.birthday
                rec.retirement_date = rec.retirement_date.replace(year=rec.birthday.year + 60)
            else:
                rec.retirement_date = False

    def create_medical_life_history(self):
        for rec in self:
            if rec.medical_line_ids:
                rec.medical_line_ids[-1].check_history_fields(date=datetime.date(2022, 1, 1))
            if rec.life_line_ids:
                rec.life_line_ids[-1].check_history_fields(date=datetime.date(2022, 1, 1))

    def get_medical_cost(self, payslip):
        for rec in self:
            payslip_date_from = payslip.dict.date_from
            if rec.medical_line_ids:
                medical_lines = rec.medical_line_ids[-1]
                cost = 0
                for medical in medical_lines:
                    if payslip_date_from <= medical.date_to:
                        cost += medical.cost
                return -1 * cost

    def get_life_cost(self, payslip):
        for rec in self:
            payslip_date_from = payslip.dict.date_from
            if rec.life_line_ids:
                life_lines = rec.life_line_ids[-1]
                cost = 0
                for life in life_lines:
                    if payslip_date_from <= life.date_to:
                        cost += life.cost
                return -1 * cost
            else:
                return 0

    @api.constrains('employee_arabic', 'employee_attendance_id')
    def concatenate_fields(self):
        for rec in self:
            rec.full_name = False
            name = rec.name or ''
            employee_attendance_id = rec.employee_attendance_id or ''
            employee_arabic = rec.employee_arabic or ''
            rec.full_name = "%s%s%s" % (name, employee_attendance_id, employee_arabic)
            rec.name = False
            rec.update({'name': rec.full_name})

    @api.depends('name', 'employee_arabic', 'employee_attendance_id')
    def name_get(self):
        res = []
        for record in self:
            name = "[%s]%s%s" % (record.employee_attendance_id or "", record.name, record.employee_arabic or "")
            res.append((record.id, name))
        return res

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = []
        if name:
            domain = ['|', '|', ('employee_attendance_id', '=ilike', name + '%'),
                      ('employee_attendance_id', operator, name),
                      ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        return super()._name_search(name, domain, operator, limit, order)

    @api.onchange('cluster_id')
    def onchange_cluster_id(self):
        for rec in self:
            rec.character_id = False
            if rec.cluster_id:
                if rec.cluster_id.character_ids:
                    rec.character_id = rec.cluster_id.character_ids[0].id
            rec.onchange_character_id()

    @api.onchange('character_id')
    def onchange_character_id(self):
        for rec in self:
            rec.title_id = False
            if rec.character_id:
                if rec.character_id.title_ids:
                    rec.title_id = rec.character_id.title_ids[0].id
            rec.onchange_title_id()

    @api.onchange('title_id')
    def onchange_title_id(self):
        for rec in self:
            rec.character_level_id = False
            if rec.title_id:
                if rec.title_id.character_level_ids:
                    rec.character_level_id = rec.title_id.character_level_ids[0].id

    @api.constrains('cluster_id')
    def constrains_cluster_id(self):
        for rec in self:
            if not rec.character_id:
                rec.onchange_cluster_id()

    @api.constrains('character_id')
    def constrains_character_id(self):
        for rec in self:
            if not rec.title_id:
                rec.onchange_character_id()

    @api.constrains('title_id')
    def constrains_title_id(self):
        for rec in self:
            if not rec.character_level_id:
                rec.onchange_title_id()

    @api.model
    def create(self, values):
        values['employee_attendance_id'] = self.env['ir.sequence'].next_by_code('hr.employee')
        fields = ['job_id', 'job_title', 'department_id', 'project_id', 'grade_id', 'sub_project',
                  'bank_account_number_id', 'bank_id', 'cluster_id', 'title_id', 'character_level_id',
                  'character_id', 'func_id', 'cost_center']
        res = super(HrEmployeeInherit, self).create(values)
        for rec in res:
            if any(field in values for field in fields):
                rec._create_preposition_entry()
        return res

    def _create_preposition_entry(self):
        for rec in self:
            data = {
                'employee_id': rec.id,
                'date_to': fields.Date.today(),
                'job': rec.job_id.name,
                'department_id': rec.department_id.name,
                'project': rec.project_id.id,
                'sub_project': rec.sub_project,
                'grade_id': rec.grade_id.id,
                'bank_name': rec.bank_id.name,
                'account_number': rec.bank_account_number_id.display_name,
                'cluster_id': rec.cluster_id.id,
                'title_id': rec.title_id.id,
                'func_id': rec.func_id.id,
                'character_id': rec.character_id.id,
                'character_level_id': rec.character_level_id.id,
                'cost_center': rec.cost_center_id.name,
            }
            self.env['hr.preposition'].create(data)

    def write(self, values):
        fields = ['job_id', 'job_title', 'department_id', 'project_id', 'grade_id', 'sub_project',
                  'bank_account_number_id', 'bank_id', 'cluster_id', 'title_id', 'character_level_id',
                  'character_id', 'func_id', 'cost_center']
        result = super(HrEmployeeInherit, self).write(values)
        for rec in self:
            if any(field in values for field in fields):
                rec._create_preposition_entry()
        return result


class InsuranceTap(models.Model):
    _name = 'insurance.tap'
    _description = 'Insurance Tap'

    social_insurance_no = fields.Char(string="Social Insurance No")
    social_insurance_office = fields.Char(string="Social Insurance Office")
    insurance_start_date = fields.Date()
    insurance_end_date = fields.Date()
    basic_insurance_salary = fields.Float()
    total_number_of_insurance_years = fields.Integer()
