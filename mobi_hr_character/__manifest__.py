# -*- coding: utf-8 -*-
{
    'name': "mobi_hr_character",

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'mobi_script_leaves', 'project', 'sh_analytic_journal', 'hr_payroll_account'],

    # always loaded
    'data': [
        'data/data_excuse.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/hr_cluster.xml',
        'views/hr_title.xml',
        'views/character_level.xml',
        'views/func_tittle.xml',
        'views/insurance_tap.xml',
        # 'views/employee_category.xml',
        'views/employee_grade.xml',
        'views/employee_division.xml',
        'views/contract.xml',
        'views/attendance.xml',
        'views/hr_leave_type.xml',
        'wizard/end_of_service_incentive.xml',
        'views/hr_termination.xml',
        'views/hr_excuse.xml',
        'views/hr_suspended.xml',
        'views/hr_medical_insurance.xml',
        'views/hr_life_insurance.xml',
        'views/hr_insurance_company.xml',
        'views/hr_employee.xml',
        'views/payment_method_employee.xml',
        'views/res_bank_custom.xml',
        'views/res_partner_bank_custom.xml',
    ],
    "license": "LGPL-3",
}
