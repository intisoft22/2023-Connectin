# -*- coding: utf-8 -*-
{
    'name': "Shopee Sync",

    'summary': "Shopee Sync ",

    'description': """
        Long description of module's purpose
    """,

    'author': "Niyuzuku",
    'category': 'Syncronization',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'sale',
        'mail',
        'mh_marketplace_account',
        'mh_shopee_product_sync'
        ],

    # always loaded
    'data': [
        'data/config.xml',
        'views/views.xml',
        'views/marketplace_account_view.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
    ],

}              
