# -*- coding: utf-8 -*-
{
    'name': "Income Tax Handicap",

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'centione_income_tax'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    "license": "LGPL-3",
}
