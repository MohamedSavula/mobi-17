# -*- coding: utf-8 -*-
{
    'name': "mobi_delivery_request",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase_request', 'hr', 'project', 'purchase'],

    # always loaded
    'data': [
        'data/centione_delivery_request_data.xml',
        'data/centione_delivery_request_sequence.xml',
        'data/mail_templates.xml',
        'data/centione_purchase_request_sequence.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'wizard/centione_process_request_views.xml',
        'wizard/products_category_approval_wizard.xml',
        'wizard/create_po.xml',
        'wizard/lines_stock_wizard.xml',
        'views/centione_delivery_request_views.xml',
        'views/centione_purchase_request_line.xml',
        'views/centione_purchase_request_views.xml',
        'views/delivery_request_settings.xml',
        'views/product_category_view.xml',
        'views/product_template_view.xml',
    ],
    "license": "LGPL-3",
}
