from odoo import fields, models, api, _
import hmac
import json
from datetime import date, datetime, timedelta
import time
import requests
import hashlib
import urllib.request
from odoo import http
import requests
from odoo.exceptions import AccessError

import requests
import logging
import base64
_logger = logging.getLogger(__name__)
import os.path
from odoo.exceptions import UserError

class MarketplaceAccount(models.Model):
    _inherit = 'marketplace.account'

    page_product = fields.Char('Page Product')

    def get_category(self):
        for rec in self:
            # self.get_token()
            timest = int(time.time())
            host = rec.url_api
            path = "/api/v2/product/get_category"
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
            access_token, partner_id, shop_id, timest, sign)
            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['shopee.product.category']
            if json_loads:
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
                else:
                    for jload in json_loads['response']['category_list']:
                        # print(jload)
                        data_ready = datas.search([('shopee_category_id', '=', jload['category_id'])])
                        parent_ready = datas.search([('shopee_category_id', '=', jload['parent_category_id'])], limit=1)
                        if parent_ready:
                            # print(parent_ready.name)
                            # print(parent_ready.id)
                            vals_product_category = {
                                'name': jload['original_category_name'],
                                'shopee_category_id': jload['category_id'],
                                'has_children': jload['has_children'],
                                'parent_category_id': jload['parent_category_id'],
                                'parent_id': parent_ready.id,
                                'display_category_name': jload['display_category_name'],
                            }
                        else:
                            # print(jload['parent_category_id'])
                            vals_product_category = {
                                'name': jload['original_category_name'],
                                'shopee_category_id': jload['category_id'],
                                'has_children': jload['has_children'],
                                'parent_category_id': jload['parent_category_id'],
                                # 'parent_id': jload['parent_category_id'],
                                'display_category_name': jload['display_category_name'],
                            }
                        if data_ready:
                            data_ready.write(vals_product_category)
                            categ_id=data_ready
                        else:
                            categ_id = datas.create(vals_product_category)
                        # if not jload['has_children']:
                        #     self.get_brand(categ_id.id, jload['category_id'], 0)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Notification"),

                    'message': 'Create Product Category',
                    # 'type': 'success',
                    'sticky': True,  # True/False will display for few seconds if false
                },
            }

    def get_brand(self, categ_id, shopee_categ_id,offset):
        for rec in self:
            print(categ_id)
            # self.get_token()
            timest = int(time.time())
            host = rec.url_api
            path = "/api/v2/product/get_brand_list"
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            datapage=100
            url = host + path + "?access_token=%s&category_id=%s&language=id&offset=%s&page_size=100&status=1&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
            access_token, shopee_categ_id,offset,partner_id, shop_id, timest, sign)
            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['shopee.brand']
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['msg']))
                else:
                    print(json_loads['response']['input_type'])
                    for jload in json_loads['response']['brand_list']:

                        data_ready = datas.search([('shopee_brand_id', '=', jload['brand_id']),('shopee_category_id', '=',shopee_categ_id)])
                        vals_product_brand = {
                            'name': jload['original_brand_name'],
                            'shopee_category_id': shopee_categ_id,
                            'categ_id': categ_id,
                            'shopee_brand_id': jload['brand_id'],
                            'display_brand_name': jload['display_brand_name'],
                        }

                        if data_ready:
                            brandid = data_ready.write(vals_product_brand)
                        else:
                            brandid = datas.create(vals_product_brand)
                    if json_loads['response']['has_next_page']:
                        self.get_brand(categ_id, shopee_categ_id, offset+datapage)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Notification"),

                    'message': 'Create Brand',
                    # 'type': 'success',
                    'sticky': True,  # True/False will display for few seconds if false
                },
            }

    def get_product(self, offset=0):
        for rec in self:
            # self.get_token()

            rec.check_expiry_token()
            timest = int(time.time())
            host = rec.url_api
            offset2 = rec.page_product
            # path = "api/v2/logistics/get_channel_list"
            path = "/api/v2/product/get_item_list"
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            itemstatus = "%5B%22NORMAL%22%5D"
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (access_token,partner_id,shop_id, timest, sign)
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&page_size=10&item_status=%s" % (access_token,partner_id,shop_id, timest, sign,itemstatus)
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&offset=0&page_size=10&item_status=NORMAL&offset=0&page_size=10&update_time_from=1611311600&update_time_to=1611311631" % (access_token,partner_id,shop_id, timest, sign)
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&offset=%s&page_size=10&item_status=NORMAl&item_status=BANNED&item_status=DELETED&item_status=UNLIST" % (
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&offset=%s&page_size=10&item_status=BANNED&item_status=UNLIST" % (
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&offset=%s&page_size=10&item_status=NORMAL&item_status=UNLIST" % (
            access_token, partner_id, shop_id, timest, sign, offset2)
            # access_token, partner_id, shop_id, timest, sign) + "&update_time_from=1672578000&update_time_to=1677675600"

            # url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get?partner_id=1023577&sign=%s&timestamp=%s" % (
            # sign, timest)
            print(url)

            payload = json.dumps({})
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            # print(response)
            json_loads = json.loads(response.text)
            print(json_loads)

            # rec.access_token_shopee = json_loads['access_token']
            return2 = []
            item_list = 'kosong'
            datas = self.env['product.template']
            if json_loads:
                if json_loads['error']:
                    return2.append(str(json_loads['message']))
                    # print(json_loads['message'])
                else:
                    if (json_loads['response']['total_count'] > 0):
                        for jload in json_loads['response']['item']:
                            if jload['item_id']:
                                if item_list == 'kosong':
                                    item_list = str(jload['item_id'])
                                else:
                                    item_list = item_list + ',' + str(jload['item_id'])
                                # self.get_model_product_detail(jload['item_id'])
                        self.get_product_detail(item_list)
                        if json_loads['response']['total_count'] > (json_loads['response']['next_offset']+10):
                            rec.page_product=json_loads['response']['next_offset']
                            # self.get_product(json_loads['response']['next_offset'])
                        else:
                            rec.page_product =0
                    else:
                        return2.append(str(json_loads['response']['total_count']))
            print(item_list)

    def get_product_detail(self, item_list):
        for rec in self:
            timest = int(time.time())
            host = rec.url_api
            path = "/api/v2/product/get_item_base_info"
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()

            url = host + path + "?item_id_list=%s&access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&need_complaint_policy=true&need_tax_info=true" % (
            item_list, access_token, partner_id, shop_id, timest, sign)
            print(url)
            payload = json.dumps({
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            # print(response.text)
            json_loads = json.loads(response.text)
            # print(json_loads)
            # rec.access_token_shopee = json_loads['access_token']
            return2 = []
            sequence = 100
            datas = self.env['product.template']
            if json_loads:
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
                else:
                    urutan=0
                    for jload in json_loads['response']['item_list']:
                        sequence += 1
                        data_ready = datas.search([('shopee_product_id', '=', jload['item_id'])])
                        category_id = False
                        shopee_category_id = False
                        shopee_category_ids = False
                        # if 'category_id' in jload:
                        #     # category_id = self.env['product.category'].search(
                        #     category_id = self.env['shopee.product.category'].search(
                        #         [('shopee_category_id', '=', jload['category_id'])]).id
                        if category_id is False:
                            category_id = self.env['product.category'].search([('name', '=', 'All')])
                        if jload['category_id']:
                            shopee_category_ids = self.env['shopee.product.category'].search([('shopee_category_id', '=', jload['category_id'])])
                            shopee_category_id = shopee_category_ids.id
                        stock = 2000
                        if 'stock_info_v2' in jload:
                            # print(jload['stock_info_v2'])
                            for sstock in jload['stock_info_v2']['seller_stock']:
                                stock = sstock['stock']
                                # print(stock)
                        price=0
                        if 'price_info'in jload:
                            price=jload['price_info'][0]['original_price']


                        vals_product = {
                            'shopee_product_id': jload['item_id'],
                            'categ_id': category_id.id,
                            'name': jload['item_name'],
                            'shopee_name': jload['item_name'],
                            'shopee_desc': jload['description'],
                            'shopee_category_id': shopee_category_id,
                            'shopee_account_id': rec.id,
                            'shopee_condition': jload['condition'],
                            'shopee_price': price,
                            'weight': jload['weight'],
                            'shopee_product_status': jload['item_status'],
                            'shopee_item_status': jload['item_status'],
                            'shopee_weight': float(jload['weight'])*1000,
                            'shopee_length': jload['dimension']['package_length'],
                            'shopee_width': jload['dimension']['package_width'],
                            'shopee_height': jload['dimension']['package_height'],
                            'shopee_sku': jload['item_sku'],
                            'shopee_stock': str(stock),
                            'sequence': sequence,
                            'type': 'product',
                            'is_shopee': True,
                        }
                        if data_ready:
                            vals_product = {
                                'shopee_product_id': jload['item_id'],
                                'shopee_name': jload['item_name'],
                                'shopee_desc': jload['description'],
                                'shopee_category_id': shopee_category_id,
                                'shopee_account_id':  rec.id,
                                'shopee_condition':  jload['condition'],
                                'shopee_price':  price,
                                'weight': jload['weight'],
                                'shopee_product_status': jload['item_status'],
                                'shopee_item_status': jload['item_status'],
                                'shopee_weight': float(jload['weight'])*1000,
                                'shopee_length': jload['dimension']['package_length'],
                                'shopee_width': jload['dimension']['package_width'],
                                'shopee_height': jload['dimension']['package_height'],
                                'shopee_sku': jload['item_sku'],
                                'shopee_stock': str(stock),
                                'is_shopee': True,
                            }
                            print('update')
                            print(vals_product)
                            data_ready.write(vals_product)
                            idproduct=data_ready
                        else:
                            print('create')
                            print(vals_product)
                            idproduct=datas.create(vals_product)
                        if shopee_category_ids:
                            idproduct.get_attribute(shopee_category_ids)
                            if 'attribute_list' in jload:
                                idproduct.set_attribute_product(jload['attribute_list'])

                            if 'logistic_info' in jload:
                                idproduct.shopee_logistic_ids =False
                                idproduct.set_logistic_product(jload['logistic_info'])
                            if 'has_model' in jload:
                                idproduct.has_model=True
                                idproduct.set_tier_variant_product()
                            if 'image' in jload:
                                no=1
                                imagearray = []

                                idproduct.shopee_image_ids =False
                                for x in jload['image']['image_url_list']:
                                    if no ==1:
                                        data = base64.b64encode(requests.get(x.strip()).content).replace(b"\n", b"")

                                        idproduct.image_1920=data
                                        no+=1
                                    else:
                                        data = base64.b64encode(requests.get(x.strip()).content).replace(b"\n", b"")

                                        vals_image_product = {
                                            'image_1920': data,

                                        }
                                        imagearray.append((0, 0, vals_image_product))


                                idproduct.shopee_image_ids =imagearray
                        urutan+=1
                        print(urutan)
                        idproduct.changevariant_shopee =False
                        idproduct.variant_ok =False

    def get_variant(self):
        for rec in self:
            datas = self.env['product.template']
            data_ready = datas.search([('shopee_account_id', '=', rec.id)])
            for prd in data_ready:
                if prd.has_model:
                    prd.set_tier_variant_product()
                    prd.changevariant_shopee = False
                    prd.variant_ok = False

    def get_order(self):
        for rec in self:
            # self.get_token()
            timest = int(time.time())
            host = rec.url_api
            path = "/api/v2/order/get_order_list"
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            time_from = str(int(datetime.timestamp(datetime.now()-timedelta(days=15))))
            time_to = str(int(datetime.timestamp(datetime.now())))
            # time_from = str(int(datetime.timestamp(datetime.now() - timedelta(days=75))))
            # time_to = str(int(datetime.timestamp(datetime.now() - timedelta(days=60))))
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&page_size=20&time_from=%s&time_range_field=create_time&time_to=%s" % (
            access_token, partner_id, shop_id, timest, sign, time_from, time_to)
            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            order_sn = 'kosong'
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['message']))
                else:
                    for jload in json_loads['response']['order_list']:
                        print(jload)
                        order_sn = jload['order_sn']
                        self.get_order_detail(order_sn)

    def get_order_time(self, start_date, end_date,cursor=False):
        for rec in self:
            # self.get_token()

            rec.check_expiry_token()
            timest = int(time.time())
            host = rec.url_api
            path = "/api/v2/order/get_order_list"
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            time_from = start_date
            time_to = end_date
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&page_size=20&time_from=%s&time_range_field=create_time&time_to=%s" % (
                access_token, partner_id, shop_id, timest, sign, time_from, time_to)
            if not cursor:
                url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&page_size=20&time_from=%s&time_range_field=create_time&time_to=%s" % (
                access_token, partner_id, shop_id, timest, sign, time_from, time_to)
            else:
                url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&page_size=20&time_from=%s&time_range_field=create_time&time_to=%s&cursor=%s" % (
                access_token, partner_id, shop_id, timest, sign, time_from, time_to,cursor)

            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            order_sn = 'kosong'
            if json_loads:
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
                else:
                    for jload in json_loads['response']['order_list']:
                        print(jload)
                        order_sn = jload['order_sn']
                        self.get_order_detail(order_sn)
                    # if json_loads['response']['next_cursor']:
                    #     self.get_order_time(start_date, end_date,cursor=json_loads['response']['next_cursor'])

    def get_order_detail(self, order_sn):
        for rec in self:
            timest = int(time.time())
            host = rec.url_api
            path = "/api/v2/order/get_order_detail"
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            # time_from = str(int(datetime.timestamp(datetime.now()-timedelta(days=15))))
            # time_to = str(int(datetime.timestamp(datetime.now())))
            add_fields = "&response_optional_fields=%5Brecipient_address%2Citem_list%2Cpackage_list%2Cbuyer_username%2Cestimated_shipping_fee%2Cpayment_method%2Cshipping_carrier%2Cnote%2Cbuyer_id%2Cpayment_method%5D"
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&order_sn_list=%s" % (
            access_token, partner_id, shop_id, timest, sign, order_sn) + add_fields
            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['sale.order']
            picking = self.env['stock.picking']
            invoice = self.env['account.move']
            if json_loads:
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
                else:
                    ada_data = False
                    for jload in json_loads['response']['order_list']:
                        product_ready = False
                        data_ready = datas.search([('client_order_ref', '=', order_sn)])
                        partner = self.env['res.partner'].search([('name', '=', 'Shopee')], limit=1)
                        shipping_address = ''
                        # address = jload['recipient_address']
                        item_list = []
                        recipient = 'kosong'
                        # if jload['recipient_address']:
                        #     recipient = str(jload['recipient_address']['name']) + ' (' + str(jload['recipient_address']['phone']) + ') /n' + str(jload['recipient_address']['full_address']) + ' /n ' + str(jload['recipient_address']['town']) + ' - ' + str(jload['recipient_address']['district']) + ' - ' + str(jload['recipient_address']['city']) + ' - ' + str(jload['recipient_address']['state']) + ' /n ' + str(jload['recipient_address']['region']) + ' /n ' + str(jload['recipient_address']['zipcode']) + ' /n '

                        for prod in jload['item_list']:
                            if prod['model_id']==0:
                                product_ready = self.env['product.product'].search([('shopee_product_id', '=', prod['item_id'])], limit=1)
                            else:
                                product_ready = self.env['product.product'].search([('shopee_model_id', '=', prod['model_id'])], limit=1)
                                if not product_ready:
                                    shopee_product_ready = self.env['shopee.model.product'].search([('model_id', '=', prod['model_id'])], limit=1)
                                    if shopee_product_ready:
                                        product_ready=shopee_product_ready[0].product_id

                            if product_ready:
                                vals_item = {
                                    'product_id': product_ready.id,
                                    'name': product_ready.name + ' (model: '+ str(prod['model_name']) + ')',
                                    'product_uom_qty': prod['model_quantity_purchased'],
                                    # 'product_qty': jload['model_quantity_purchased'],
                                    'price_unit': prod['model_original_price'],
                                    'shopee_model_original_price': prod['model_original_price'],
                                    'shopee_model_discounted_price': prod['model_discounted_price'],
                                }
                                item_list.append(vals_item)


                        vals_order = {
                            'partner_id': partner.id,
                            'client_order_ref': jload['order_sn'],
                            'date_order': datetime.fromtimestamp(int(jload['create_time'])).strftime('%Y-%m-%d %H:%M:%S'),
                            # 'date_order': datetime.fromtimestamp(int(jload['create_time'])),
                            'note': jload['note'],
                            'shopee_recipient_address': recipient,
                            'shopee_buyer_username' : jload['buyer_username'],
                            'shopee_buyer_id': jload['buyer_id'],
                            'shopee_message_to_seller': jload['message_to_seller'],
                            'shopee_order_status': jload['order_status'],
                            'shopee_payment_method': jload['payment_method'],
                            'shopee_shipping_carrier': jload['shipping_carrier'],
                            'marketplace_account_id': rec.id,
                        }
                        status = jload['order_status']

                        print(vals_order)
                        so_id = False
                        if data_ready:
                            if (data_ready.state != 'done') and (data_ready.state != 'sale'):
                                print('update')
                                updated = data_ready.write(vals_order)
                                ada_data = True
                                for prod in jload['item_list']:
                                    if prod['model_id'] == 0:
                                        product_ready = self.env['product.product'].search([('shopee_product_id', '=', prod['item_id'])], limit=1)
                                    else:
                                        product_ready = self.env['product.product'].search([('shopee_model_id', '=', prod['model_id'])], limit=1)
                                        if not product_ready:
                                            shopee_product_ready = self.env['shopee.model.product'].search(
                                                [('model_id', '=', prod['model_id'])], limit=1)
                                            if shopee_product_ready:
                                                product_ready = shopee_product_ready[0].product_id
                                    if product_ready:
                                        vals_item = {
                                            'product_id': product_ready.id,
                                            'name': product_ready.name + ' (model: '+ str(prod['model_name']) + ')',
                                            'product_uom_qty': prod['model_quantity_purchased'],
                                            'price_unit': prod['model_original_price'],
                                            'shopee_model_original_price': prod['model_original_price'],
                                            'shopee_model_discounted_price': prod['model_discounted_price'],
                                            # 'invoiced_price': prod['invoiced_price'],
                                            'order_id': data_ready.id
                                        }
                                        print(vals_item)
                                        item_ready = False
                                        for line in data_ready.order_line:
                                            if line.product_id.shopee_product_id == str(prod['item_id']):
                                                wr = line.write(vals_item)
                                                item_ready = True
                                        print(item_ready)
                                        if not item_ready:
                                            print('create')
                                            create_line = self.env['sale.order.line'].create(vals_item)
                                            print(create_line)
                                if jload['order_status'] != 'CANCELLED':
                                    data_ready.action_confirm()
                                else:
                                    data_ready.action_cancel()

                            else:
                                vals_order = {
                                    'date_order': datetime.fromtimestamp(int(jload['create_time'])).strftime(
                                        '%Y-%m-%d %H:%M:%S'),
                                    'note': jload['note'],
                                    'shopee_recipient_address': recipient,
                                    'shopee_buyer_username': jload['buyer_username'],
                                    'shopee_buyer_id': jload['buyer_id'],
                                    'shopee_message_to_seller': jload['message_to_seller'],
                                    'shopee_order_status': jload['order_status'],
                                    'shopee_payment_method': jload['payment_method'],
                                    'shopee_shipping_carrier': jload['shipping_carrier'],
                                    'marketplace_account_id': rec.id,
                                }
                                data_ready.write(vals_order)
                                if jload['order_status'] == 'CANCELLED':
                                    picking_ready = picking.search([('origin', '=', data_ready.name)])
                                    if picking_ready:
                                        if picking_ready.state == 'done':
                                            picking_ready.action_toggle_is_locked()
                                            move_ready = self.env['stock.move'].search([('picking_id', '=', picking_ready.id)])
                                            for move in move_ready:
                                                move.write({'quantity_done':0})
                                            picking_ready.action_toggle_is_locked()
                            so_id = data_ready
                        else:
                            print("vals orer ================")
                            print(vals_order)
                            created = datas.create(vals_order)
                            print(created)
                            for prod in jload['item_list']:
                                note = ''
                                if prod['model_id'] == 0:
                                    product_ready = self.env['product.product'].search([('shopee_product_id', '=', prod['item_id'])], limit=1)
                                else:
                                    product_ready = self.env['product.product'].search([('shopee_model_id', '=', prod['model_id'])], limit=1)
                                    if not product_ready:
                                        shopee_product_ready = self.env['shopee.model.product'].search(
                                            [('model_id', '=', prod['model_id'])], limit=1)
                                        if shopee_product_ready:
                                            product_ready = shopee_product_ready[0].product_id
                                if product_ready:
                                    item_ready = False
                                    vals_item = {
                                        'product_id': product_ready.id,
                                        'name': product_ready.name + ' (model: '+ str(prod['model_name']) + ')',
                                        'product_uom_qty': prod['model_quantity_purchased'],
                                        'price_unit': prod['model_original_price'],
                                        'shopee_model_original_price': prod['model_original_price'],
                                        'shopee_model_discounted_price': prod['model_discounted_price'],
                                        'order_id': created.id
                                    }
                                    for line in data_ready.order_line:
                                        if line.product_id.shopee_product_id == str(prod['item_id']):
                                            wr = line.write(vals_item)
                                            item_ready = True
                                    if not item_ready:
                                        create_line = self.env['sale.order.line'].create(vals_item)
                                else:
                                    note += 'Produk (' + str(prod['item_id']) + ' : ' + str(prod['item_name']) + ') sudah dihapus atau belum tersinkronisasi. /n'
                                    updated = created.write({'note': note})

                            if jload['order_status'] != 'CANCELLED':
                                created.action_confirm()
                                so_id = created
                            else:
                                created.action_cancel()
                                print("masuk siniiiiii")

                        # SEBELUMNYA ACTIVE
                        if so_id:
                            if so_id.order_line:
                                for pack in jload['package_list']:
                                    vals_pack = {
                                        'package_number': pack['package_number'],
                                        'logistics_status': pack['logistics_status'],
                                        'shipping_carrier': pack['shipping_carrier'],
                                        'order_id': so_id.id
                                    }
                                    package = self.env['shopee.packege.list']
                                    pack_ready = package.search([('package_number', '=', pack['package_number'])])
                                    if pack_ready:
                                        pack_ready.write(vals_pack)
                                        # for pitem in pack['item_list']:
                                        #     pitem_ready = self.env['product.product'].search(
                                        #         [('shopee_product_id', '=', str(pitem['item_id']))], limit=1)
                                        #     if pitem_ready:
                                        #         vals_pack_item = {
                                        #             'product_id': pitem_ready.id,
                                        #             'model_id': pitem['model_id'],
                                        #             'quantity': pitem['model_quantity'],
                                        #             'pack_id': pack_ready.id
                                        #         }
                                        #         pack_ready = self.env['shopee.packege.list.detail'].create(vals_pack_item)

                                    else:
                                        pack_ready = package.create(vals_pack)

          
                            picking_ready = picking.search([('origin', '=', so_id.name)])
                            if picking_ready:
                                if picking_ready.state != 'done':
                                    picking_ready.scheduled_date =datetime.fromtimestamp(int(jload['ship_by_date'])).strftime(
                                            '%Y-%m-%d %H:%M:%S')
                                if picking_ready.state != 'done':
                                    for pline in picking_ready.move_ids_without_package:
                                        # if pline.product_uom_qty == pline.forecast_availability:
                                        pline.write({'quantity_done':pline.forecast_availability})
                                    picking_ready.button_validate()

                                    picking_ready.date_done =datetime.fromtimestamp(int(jload['ship_by_date'])).strftime(
                                            '%Y-%m-%d %H:%M:%S')
                                so_id.get_escrow_detail()
                                # invoice_ready = invoice.search([('ref', '=', so_id.client_order_ref)])
                                # if not invoice_ready and so_id.partner_id and so_id.partner_id.property_account_receivable_id:
                                #     context = {
                                #         'active_model': 'sale.order',
                                #         'active_ids': [so_id.id],
                                #         'active_id': so_id.id,
                                #     }
                                #     payment = self.env['sale.advance.payment.inv'].with_context(context).create({'advance_payment_method': 'delivered'})
                                #     payment.create_invoices()
                                #     invoice_ready = invoice.search([('ref', '=', so_id.client_order_ref)])
                                # print(invoice_ready)
                        # SEBELUMNYAACTIVE
                                # for inv in invoice_ready:
                                #     print(inv)
                                #     if inv.state == 'draft':
								#
                                #         if status in {'READY_TO_SHIP','PROCESSED','SHIPPED','COMPLETED'}:
                                #             inv.action_post()

    def get_logistic(self):
        for rec in self:
            # self.get_token()
            timest = int(time.time())
            host = rec.url_api
            path = "/api/v2/logistics/get_channel_list"
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
            access_token, partner_id, shop_id, timest, sign)
            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['shopee.logistic']
            if json_loads:
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
                else:
                    for jload in json_loads['response']['logistics_channel_list']:
                        # print(jload)
                        data_ready = datas.search([('shopee_logistic_id', '=', jload['logistics_channel_id']),('shop_account_id', '=', rec.id)])

                        vals_logistic = {
                            'name': jload['logistics_channel_name'],
                            'desc': jload['logistics_description'],
                            'enable': jload['enabled'],
                            'shopee_logistic_id': jload['logistics_channel_id'],
                            'mask_channel_id': jload['mask_channel_id'],
                            'shop_account_id': rec.id,
                            'fee_type': jload['fee_type'],
                            'cod_enabled': jload['cod_enabled'],
                        }

                        if data_ready:
                            data_ready.write(vals_logistic)
                            log_id=data_ready
                        else:
                            log_id = datas.create(vals_logistic)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Notification"),

                    'message': 'Create Product Category',
                    # 'type': 'success',
                    'sticky': True,  # True/False will display for few seconds if false
                },
            }
        
    def get_dependencies(self):
        for rec in self:

            rec.check_expiry_token()
            rec.get_category()
            rec.get_logistic()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Notification"),

                    'message': 'Create Dependencies (Product Category,Brand, Logistic)',
                    # 'type': 'success',
                    'sticky': True,  # True/False will display for few seconds if false
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }

    def get_all_escrow(self):
        # self.get_token()
        order_ready = self.env['sale.order'].search([('shopee_order_status', '!=', False)])
        for order in order_ready:
            self.get_escrow_detail(order=order)

    def get_escrow_detail(self, order=False):
        for rec in self:
            if order:
                timest = int(time.time())
                host = rec.url_api
                path = "/api/v2/payment/get_escrow_detail"
                partner_id = rec.partner_id_shopee
                shop_id = rec.shop_id_shopee
                access_token = rec.access_token_shopee
                tmp = rec.partner_key_shopee
                partner_key = tmp.encode()
                tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
                base_string = tmp_base_string.encode()
                sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
                time_from = str(int(datetime.timestamp(datetime.now()-timedelta(days=15))))
                time_to = str(int(datetime.timestamp(datetime.now())))
                url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&order_sn=%s" % (
                access_token, partner_id, shop_id, timest, sign, order.client_order_ref)
                print(url)
                payload = json.dumps({})
                headers = {'Content-Type': 'application/json'}
                response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
                print(response.text)
                json_loads = json.loads(response.text)
                datas = self.env['account.move']
                if json_loads:
                    if json_loads['error'] == 'error_param':
                        return2.append(str(json_loads['message']))
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
                        order.write(vals_invoiced)
                        picking_ready = self.env['stock.picking'].search([('origin', '=', order.name)])
                        if picking_ready:
                            if picking_ready.state == 'done':
                                invoice_ready = datas.search([('ref', '=', order.client_order_ref)])
                                if not invoice_ready and order.partner_id and order.partner_id.property_account_receivable_id:
                                    context = {
                                        'active_model': 'sale.order',
                                        'active_ids': [order.id],
                                        'active_id': order.id,
                                    }
                                    payment = self.env['sale.advance.payment.inv'].with_context(context).create(
                                        {'advance_payment_method': 'delivered'})
                                    payment.create_invoices()
                                    invoice_ready = datas.search([('ref', '=', order.client_order_ref)])
                                    print(invoice_ready)
                                    for inv in invoice_ready:
                                        account_ready = inv.partner_id.reconcile_account_id.id
                                        if not account_ready:
                                            account_ready = self.env['account.account'].search([('code', '=', '1-111001')]).id
                                        print(inv)
                                        if inv.state == 'draft':
                                            if order.shopee_order_status in {'READY_TO_SHIP', 'PROCESSED', 'SHIPPED', 'COMPLETED'}:
                                                inv.action_post()
                                        if (inv.state == 'posted') and (inv.payment_state != 'paid'):
                                            payment = self.env['account.payment.register'].with_context(active_model='account.move',
                                                                                                        active_ids=[invoice_ready.id]).create(
                                                {
                                                    'amount': escrow_amount,
                                                    'payment_date': '2017-01-01',
                                                    'payment_difference_handling': 'reconcile',
                                                    'writeoff_account_id': account_ready,
                                                })._create_payments()

                        # for jload in json_loads['response']['order_income']:
                        #     print(jload)
                        #     partner = self.env['res.partner'].search([('name', '=', 'Shopee')], limit=1)
                        #     if partner:
                        #         vals_payout = {
                        #             'partner_id': partner.id,
                        #             'payment_type': 'inbound',
                        #             'partner_type': 'customer',
                        #             'amount': jload['payout_amount'],
                        #             'date': jload['escrow_release_time'],
                        #             'payout_amount': jload['payout_amount'],
                        #             'payout_time': jload['escrow_release_time'],
                        #             'payee_id': jload['order_sn'],
                        #         }
						#
                        #         print(jload['escrow_release_time'])
                        #         print(datetime.utcfromtimestamp(int(jload['escrow_release_time'])).strftime('%Y-%m-%d %H:%M:%S'))
                        #         # data_ready = datas.search([('ref', '=', jload['order_sn'])])
						#
                        #         order_ready = self.env['sale.order'].search([('client_order_ref', '=', jload['order_sn'])])
                        #         if order_ready:
                        #             invoice_ready = datas.search([('ref', '=', order_ready                                                                              .client_order_ref)])
                        #             if not invoice_ready and order_ready.partner_id and order_ready.partner_id.property_account_receivable_id:
                        #                 context = {
                        #                     'active_model': 'sale.order',
                        #                     'active_ids': [order_ready.id],
                        #                     'active_id': order_ready.id,
                        #                 }
                        #                 payment = self.env['sale.advance.payment.inv'].with_context(context).create(
                        #                     {'advance_payment_method': 'delivered'})
                        #                 payment.create_invoices()
                        #                 invoice_ready = invoice.search([('ref', '=', order_ready.client_order_ref)])
                        #             print(invoice_ready)
                        #             for inv in invoice_ready:
                        #                 print(inv)
                        #                 if inv.state == 'draft':
                        #                     if status in {'READY_TO_SHIP', 'PROCESSED', 'SHIPPED', 'COMPLETED'}:
                        #                         inv.action_post()
                        #             if invoice_ready:
                        #                 payment = self.env['account.payment.register'].with_context(active_model='account.move',
                        #                                                                             active_ids=[invoice_ready.id]).create(
                        #                     {
                        #                         'amount': jload['payout_amount'],
                        #                         'payment_date': '2017-01-01',
                        #                     })._create_payments()
						#
                        #                 # data_ready.write(vals_payout)
                        # if json_loads['response']['more'] == 'true':
                        #     self.get_payout_detail(page+1)

    @api.model
    def _get_order(self):
        today = date.today()
        # print(today)
        ma_ids = self.env['marketplace.account'].search(
            [('active', '=', True), ('state', '=', 'authenticated')])

        for ma in ma_ids:
            print(ma.name)
            # ma.get_token()
            ma.check_expiry_token()
            now=datetime.now()
            start_date = str(int(datetime.timestamp(ma.date_updated)))
            end_date = str(int(datetime.timestamp( (datetime.now()))))
            ma.get_order_time(start_date, end_date)
            ma.date_updated=now

