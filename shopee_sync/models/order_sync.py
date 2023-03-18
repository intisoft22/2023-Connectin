# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import xlwt, xlsxwriter
import base64
import time
from datetime import datetime, timedelta, date
from time import strptime
import math

import hmac
import hashlib
import urllib.request
from odoo import http
from odoo.exceptions import AccessError
import requests
import json


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

    shopee_order_item_id = fields.Char('Shopee Order Item ID')
    shopee_model_id = fields.Char('Model ID')
    shopee_model_original_price = fields.Float('Original Price')
    shopee_model_discounted_price = fields.Float('Discounted Price')
    shopee_invoiced_price = fields.Float('Invoiced Price')


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


class StockMove(models.Model):
    _inherit = 'stock.move'

    def write(self, vals):
        qty = 0
        if vals.get('state'):
            if (vals.get('state') == 'done') or (vals.get('state') == 'cancel'):
                for prod in self.product_id:
                    product_id = prod.id
                    if vals.get('product_id'):
                        product_id = self.vals.get('product_id')
                    product = self.env['product.product'].search([('id', '=', product_id)], order="name")
                    if product and product.shopee_product_id:
                        qty = product.qty_available
                        print('--up stock--')
                        print(product.name)
                        print(product.qty_available)
                        print(qty)
                        maccount = self.env['marketplace.account'].search([('active', '=', True)])
                        for rec in maccount:
                            timest = int(time.time())
                            host = rec.url_api
                            path = "/api/v2/product/update_stock"
                            partner_id = rec.partner_id_shopee
                            shop_id = rec.shop_id_shopee
                            access_token = rec.access_token_shopee
                            tmp = rec.partner_key_shopee
                            partner_key = tmp.encode()
                            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
                            base_string = tmp_base_string.encode()
                            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
                            datapage = 100
                            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
                                access_token, partner_id, shop_id, timest, sign)
                            print(url)

                            # payload = json.dumps({
                            #     "item_id": product.shopee_product_id,
                            #     "stock_list": [
                            #         {   "model_id": 0,
                            #             "seller_stock": [
                            #                 {   "location_id": "-",
                            #                     "stock": 0
                            #                 }
                            #             ]
                            #         }]})
                            payload = json.dumps({
                                "item_id": int(product.shopee_product_id),
                                "stock_list": [
                                    {   "model_id": 0,
                                        "seller_stock": [
                                            {   "stock": int(product.qty_available)
                                                }
                                        ]
                                        }]})
                            headers = {'Content-Type': 'application/json'}
                            response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
                            print(payload)
                            # print(response.text)
                            json_loads = json.loads(response.text)
                            return2 = []
                            messgs = '-'
                            if json_loads:
                                if json_loads['error'] == 'error_param':
                                    return2.append(str(json_loads['msg']))
                                else:
                                    print(json_loads['response'])
                                    for jload in json_loads['response']['failure_list']:
                                        # print(jload['model_id'])
                                        messgs = jload['failed_reason']
                                    for jload in json_loads['response']['success_list']:
                                        # print(json_loads)
                                        messgs = 'success'
        res = super(StockMove, self).write(vals)
        return res


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

