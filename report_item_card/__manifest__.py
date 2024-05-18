# -*- coding: utf-8 -*-
{
    'name': "Report Item Card",
    'summary': "report_item_card",
    'description': """report_item_card""",
    'author': "M.Saber",
    'category': 'stock',
    'version': '0.1',
    'depends': ['base', 'stock', 'report_xlsx', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/template.xml',
        'views/views.xml',
    ],
    "license": "LGPL-3",
}
