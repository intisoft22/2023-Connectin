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

from odoo.exceptions import UserError

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

    shopee_invoiced_price = fields.Float('Invoiced Price')
    shopee_buyer_username = fields.Char('Buyer Username')
    shopee_buyer_id = fields.Char('Buyer ID')
    shopee_recipient_address = fields.Text('Recipient Address')
    shopee_message_to_seller = fields.Text('Message from Buyer')
    shopee_order_status = fields.Char('Shopee Order Status')
    shopee_payment_method = fields.Char('Shopee Payment Method')
    shopee_shipping_carrier = fields.Char('Shopee Shipping Carrier')
    shopee_package_list = fields.One2many('shopee.packege.list', 'order_id', 'Shopee Package')
    marketplace_account_id = fields.Many2one('marketplace.account', string='Marketplace Account')

    def _prepare_confirmation_values(self):
        return {
            'state': 'sale',
        }


    def get_escrow_detail(self):
        for rec in self:
            timest = int(time.time())
            host = rec.marketplace_account_id.url_api
            path = "/api/v2/payment/get_escrow_detail"
            partner_id = rec.marketplace_account_id.partner_id_shopee
            shop_id = rec.marketplace_account_id.shop_id_shopee
            access_token = rec.marketplace_account_id.access_token_shopee
            tmp = rec.marketplace_account_id.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&order_sn=%s" % (
            access_token, partner_id, shop_id, timest, sign, rec.client_order_ref)
            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            datas = self.env['account.move']
            if json_loads:
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
                elif json_loads['error'] == 'order_not_found':
                    print('order not foud')
                else:
                    print(json_loads['response']['order_sn'])
                    # print(json_loads['response']['order_income'])
                    print(json_loads['response']['order_income']['escrow_amount'])
                    escrow_amount = json_loads['response']['order_income']['escrow_amount']
                    vals_invoiced = {
                        'shopee_invoiced_price': escrow_amount
                    }
                    rec.write(vals_invoiced)
                    picking_ready = self.env['stock.picking'].search([('origin', '=', rec.name)])
                    if picking_ready:
                        if picking_ready.state == 'done':
                            invoice_ready = datas.search([('ref', '=', rec.client_order_ref)])
                            if not invoice_ready and rec.partner_id and rec.partner_id.property_account_receivable_id:
                                context = {
                                    'active_model': 'sale.order',
                                    'active_ids': [rec.id],
                                    'active_id': rec.id,
                                }
                                payment = self.env['sale.advance.payment.inv'].with_context(context).create(
                                    {'advance_payment_method': 'delivered'})
                                payment.create_invoices()
                                invoice_ready = datas.search([('ref', '=', rec.client_order_ref)])
                                print(invoice_ready)
                                for inv in invoice_ready:
                                    inv.invoice_date=rec.date_order
                                    account_ready = inv.partner_id.reconcile_account_id.id
                                    if not account_ready:
                                        account_ready = self.env['account.account'].search([('code', '=', '1-111001')]).id
                                    print(inv)
                                    if inv.state == 'draft':
                                        if rec.shopee_order_status in {'READY_TO_SHIP', 'PROCESSED', 'SHIPPED', 'COMPLETED'}:
                                            inv.action_post()
                                    if (inv.state == 'posted') and (inv.payment_state != 'paid'):
                                        payment_ids=self.env['account.payment.register']
                                        vals_payment={ 'amount': escrow_amount,
                                                'payment_date': rec.date_order,
                                                'payment_difference_handling': 'reconcile',
                                                'writeoff_account_id': account_ready,
                                            }
                                        payment = payment_ids.with_context(active_model='account.move',active_ids=[invoice_ready.id]).create(vals_payment)._create_payments()
                            else:
                                for inv in invoice_ready:
                                    inv.invoice_date=rec.date_order
                                    account_ready = inv.partner_id.reconcile_account_id.id
                                    if not account_ready:
                                        account_ready = self.env['account.account'].search([('code', '=', '1-111001')]).id
                                    print(inv)
                                    if inv.state == 'draft':
                                        if rec.shopee_order_status in {'READY_TO_SHIP', 'PROCESSED', 'SHIPPED', 'COMPLETED'}:
                                            inv.action_post()
                                    if (inv.state == 'posted') and (inv.payment_state != 'paid'):
                                        payment_ids=self.env['account.payment.register']
                                        vals_payment={ 'amount': escrow_amount,
                                                'payment_date': rec.date_order,
                                                'payment_difference_handling': 'reconcile',
                                                'writeoff_account_id': account_ready,
                                            }
                                        payment = payment_ids.with_context(active_model='account.move',active_ids=[invoice_ready.id]).create(vals_payment)._create_payments()

# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     def write(self, vals):
#         qty = 0
#
#         if vals.get('state'):
#             if (vals.get('state') == 'done') or (vals.get('state') == 'cancel'):
#                 for prod in self.product_id:
#                     product_id = prod.id
#                     if vals.get('product_id'):
#                         product_id = self.vals.get('product_id')
#                     product = self.env['product.product'].search([('id', '=', product_id)], order="name")
#                     if product and product.shopee_product_id:
#                         qty = product.qty_available
#                         print('--up stock--')
#                         print(product.name)
#                         print(product.qty_available)
#                         print(qty)
#                         maccount = self.env['marketplace.account'].search([('active', '=', True)])
#                         for rec in product.shopee_account_id:
#
#                             rec.get_token()
#                             timest = int(time.time())
#                             host = rec.url_api
#                             path = "/api/v2/product/update_stock"
#                             partner_id = rec.partner_id_shopee
#                             shop_id = rec.shop_id_shopee
#                             access_token = rec.access_token_shopee
#                             tmp = rec.partner_key_shopee
#                             partner_key = tmp.encode()
#                             tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
#                             base_string = tmp_base_string.encode()
#                             sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
#                             datapage = 100
#                             url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
#                                 access_token, partner_id, shop_id, timest, sign)
#                             print(url)
#                             modelid=0
#                             if product.shopee_model_id != 0:
#                                 modelid=int(product.shopee_model_id)
#                             payload = json.dumps({
#                                 "item_id": int(product.shopee_product_id),
#                                 "stock_list": [
#                                     {
#                                         "model_id": modelid,
#                                         "seller_stock": [
#                                             {
#                                                 "stock": int(product.qty_available)
#                                             }
#                                         ]
#                                     }
#                                 ]
#                             })
#                             headers = {'Content-Type': 'application/json'}
#                             # response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
#                             # print(payload)
#                             # # print(response.text)
#                             # json_loads = json.loads(response.text)
#                             # return2 = []
#                             # messgs = '-'
#                             # if json_loads:
#                             #     if json_loads['error'] == 'error_param':
#                             #         return2.append(str(json_loads['msg']))
#                             #     else:
#                             #         print(json_loads['response'])
#                             #         for jload in json_loads['response']['failure_list']:
#                             #             print(jloads['model_id'])
#                             #             messgs = jloads['failed_reason']
#                             #         for jload in json_loads['response']['success_list']:
#                             #             print(json_loads)
#                             #             messgs = 'success'
#                             response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
#                             print(payload)
#                             # print(response.text)
#                             json_loads = json.loads(response.text)
#                             return2 = []
#                             messgs = '-'
#                             if json_loads:
#                                 if json_loads['error'] != '':
#                                     raise UserError(_(str(json_loads['message'])))
#                                 else:
#                                     print(json_loads['response'])
#                                     for jload in json_loads['response']['failure_list']:
#                                         # print(jload['model_id'])
#                                         messgs = jload['failed_reason']
#
#                                         raise UserError(_(str(messgs)))
#                                     for jload in json_loads['response']['success_list']:
#                                         # print(json_loads)
#                                         messgs = 'success'
# # >>>>>>> 3a3d51c091a4068b90ceb2451db48f8e0a8dc083
#         res = super(StockMove, self).write(vals)
#         return res
#

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

