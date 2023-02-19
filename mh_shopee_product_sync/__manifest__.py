# -*- coding: utf-8 -*-
{
    'name': 'Module Marketplace',
    'version': '14.0',
    'summary': 'Module Marketplace Syncronization',
    'description': 'Module Marketplace Syncronization',
    'category': 'Syncronization',
    'author': 'Meyrina (Tutor:Niyuzuku)',
    'website': 'rexmey.com',

    'depends': [
        'product','web_domain_field'
        ],

    'data': [
        'views/product.xml',
        'views/shopee_product_category_view.xml',
        'views/shopee_brand_view.xml',
        'views/shopee_logistic_view.xml',
        'views/shopee_attribute_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False

}              
