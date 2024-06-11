# -*- coding: utf-8 -*-
{
    'name': "reconcile_edit_amount",
    'depends': ['base','account_accountant','account'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'reconcile_edit_amount/models/static/src/js/r.js'

            ]}

}
