# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import xlwt, xlsxwriter
import base64
import time
from datetime import datetime, timedelta, date
from time import strptime
import math


class ShopeePackageListDetail(models.Model):
    _name = 'shopee.packege.list.detail'

    product_id = fields.Many2one('product.product', string='Product')
    model_id = fields.Char('Model ID')
    quantity = fields.Char('Quantity')
    pack_id = fields.Many2one('shopee.packege.list.detail', string='Package')


class ShopeePackageList(models.Model):
    _name = 'shopee.packege.list'

    package_number = fields.Char('Package Number')
    logistics_status = fields.Char('Logistics Status')
    shipping_carrier = fields.Char('Shipping Carrier')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    item_list = fields.One2many('shopee.packege.list.detail', 'pack_id', 'Package List')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_item_id = fields.Char('Shopee Order Item ID')
    model_id = fields.Char('Model ID')
    model_original_price = fields.Float('Original Price')
    model_discounted_price = fields.Float('Discounted Price')
    invoiced_price = fields.Float('Invoiced Price')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shopee_buyer_username = fields.Char('Buyer Username')
    shopee_buyer_id = fields.Char('Buyer ID')
    shopee_recipient_address = fields.Text('Recipient Address')
    shopee_message_to_seller = fields.Text('Message from Buyer')
    shopee_order_status = fields.Char('Shopee Order Status')
    shopee_payment_method = fields.Char('Shopee Payment Method')
    shopee_shipping_carrier = fields.Char('Shopee Shipping Carrier')
    shopee_package_list = fields.One2many('shopee.packege.list', 'order_id', 'Shopee Package')


class ShopeeGetOrder(models.TransientModel):
    _name = 'shopee.get.order'
    _description = 'Shopee Get Order'

    def get_default_date_start(self):
        date_now = (datetime.now()-timedelta(days=14))
        return date_now

    def get_default_date_end(self):
        date_now = (datetime.now())
        return date_now

    start_date = fields.Datetime('Start Date', default=get_default_date_start, required=True)
    end_date = fields.Datetime('End Date', default=get_default_date_end, required=True)
    marketplace_account_id = fields.Many2one('marketplace.account', string='Marketplace Account', required=True)

    def get_shopee_order(self):
        for o in self:
            if o.marketplace_account_id:
                acc = self.env['marketplace.account'].search([('id', '=', o.marketplace_account_id.id)], order="name")
                if o.start_date and o.end_date:
                    start_date = str(int(datetime.timestamp(o.start_date)))
                    end_date = str(int(datetime.timestamp(o.end_date)))
                    acc.get_order_time(start_date,end_date)
                    print('get order done')
        return True

