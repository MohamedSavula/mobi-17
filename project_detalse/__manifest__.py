# -*- coding: utf-8 -*-
{
    'name': "project_detalse",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'account_accountant', 'analytic_account_location'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],

}
