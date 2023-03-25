# -*- coding: utf-8 -*-

import json
import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta

# from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

# headers = {
#     'Content-Type': "application/json",
#     'Accept': "application/json",
#     'Cache-Control': "no-cache",
#     'Forca-Token': "ec953a02-4f1a-4ad9-b257-1b43a4629a2c"
# }

headers = {
    'Content-Type': "application/json",
    'Accept': "application/json",
    'Cache-Control': "no-cache",
}

header2 = {
    'Content-Type': "application/x-www-form-urlencoded",
    'Accept': "application/json",
    'Cache-Control': "no-cache",
}


class ResPartner(models.Model):
    _inherit = 'res.partner'

    marketplace_account_id = fields.Many2one('marketplace.account', string='Marketplace Account')
    reconcile_account_id = fields.Many2one('account.account', string='Reconcile Account')

class ProductCategory(models.Model):
    _inherit = 'product.category'

    shopee_category_id = fields.Integer('Shopee Category ID')
    parent_category_id = fields.Char('Shopee Parent Category ID')
    display_category_name = fields.Char('Shopee Display Category Name')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopee_stock = fields.Char('Shopee Stock')
    shopee_product_id = fields.Char('Shopee Product ID')
    shopee_product_status = fields.Char('Shopee Product Status')

