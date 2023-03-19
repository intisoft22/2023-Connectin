# -*- coding: utf-8 -*-
{
    'name': 'Module Report',
    'version': '14.0',
    'summary': 'Module Report',
    'description': 'Module Report',
    'author': 'Mifta',
    'website': '',
    'depends': [
        'mh_marketplace_account',
        'account',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_report_view.xml',
        'report/report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}
