# -*- coding: utf-8 -*-
{
    'name': 'Inter Warehouse Transfer App',
    "author": "Edge Technologies",
    'version': '1.0',
    'live_test_url': "https://youtu.be/serevBlq2z4",
    "images": ['static/description/main_screenshot.png'],
    'summary': "Inter warehouse transfer warehouse inter transfer internal warehouse transfer warehouse internal transfer for multi warehouse internal transfer multi warehouse internal transfer multi warehouse stock transfer for multi warehouse stock movement warehouse.",
    'description': """ 
        Generate inter warehouse transfer according configured source location to transit location and transit location to destination location, approve transfer by inventory manager.
    """,
    "license": "LGPL-3",
    'depends': ['stock'],
    'data': [
        'data/inter_warehouse_seq.xml',
        'security/ir.model.access.csv',
        'views/inter_warehouse_transfer.xml',
        'views/res_config_setting.xml',
    ],
    'category': 'Warehouse',
}
