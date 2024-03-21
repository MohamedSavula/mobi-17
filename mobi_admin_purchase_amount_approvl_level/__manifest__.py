# -*- coding: utf-8 -*-
{
    'name': "mobi_admin_purchase_amount_approvl_level",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'purchase', 'contacts', 'account'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/purchase_amount_user.xml',
        'views/purchase_order_inherit.xml',
        'views/chart_of_account.xml',
    ],
    "license": "LGPL-3",
}