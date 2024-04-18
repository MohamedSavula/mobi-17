# -*- coding: utf-8 -*-
{
    'name': "inventory_aging_excel_report",
    'author': "Centione",
    'website': "http://www.centione.com",
    'category': 'Stock',
    'version': '0.1',
    'depends': ['base', 'project', 'stock', 'product', 'mobi_location_flag', 'mobi_admin_stock_force_date'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
