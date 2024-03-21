# -*- coding: utf-8 -*-
{
    'name': "mobi_product_cost_log",
    'author': "Centione",
    'website': "http://www.centione.com",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'product', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    "license": "LGPL-3",
}
