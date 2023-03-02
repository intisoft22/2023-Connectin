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


class MarketplaceAccount(models.Model):
    _inherit = 'marketplace.account'

    def get_category(self):
        for rec in self:
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
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['msg']))
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
            timest = int(time.time())
            host = rec.url_api
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
            access_token, partner_id, shop_id, timest, sign, offset)
            # access_token, partner_id, shop_id, timest, sign) + "&update_time_from=1672578000&update_time_to=1677675600"

            # url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get?partner_id=1023577&sign=%s&timestamp=%s" % (
            # sign, timest)
            print(url)

            payload = json.dumps({})
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            print(response)
            print(response.text)
            json_loads = json.loads(response.text)

            # rec.access_token_shopee = json_loads['access_token']
            return2 = []
            item_list = 'kosong'
            datas = self.env['product.template']
            if json_loads:
                if json_loads['error']:
                    return2.append(str(json_loads['message']))
                    print(json_loads['message'])
                else:
                    if (json_loads['response']['total_count'] > 0):
                        for jload in json_loads['response']['item']:
                            if jload['item_id']:
                                if item_list == 'kosong':
                                    item_list = str(jload['item_id'])
                                else:
                                    item_list = item_list + ',' + str(jload['item_id'])
                        self.get_product_detail(item_list)
                        if json_loads['response']['total_count'] > (json_loads['response']['next_offset']+10):
                            self.get_product(json_loads['response']['next_offset'])
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
            print(json_loads)
            # rec.access_token_shopee = json_loads['access_token']
            return2 = []
            sequence = 100
            datas = self.env['product.template']
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['msg']))
                else:
                    for jload in json_loads['response']['item_list']:
                        sequence += 1
                        data_ready = datas.search([('shopee_product_id', '=', str(jload['item_id']))])
                        category_id = False
                        # if 'category_id' in jload:
                        #     # category_id = self.env['product.category'].search(
                        #     category_id = self.env['shopee.product.category'].search(
                        #         [('shopee_category_id', '=', jload['category_id'])]).id
                        if category_id is False:
                            category_id = self.env['product.category'].search([('name', '=', 'All')])
                        vals_product = {
                            'shopee_product_id': str(jload['item_id']),
                            'categ_id': category_id.id,
                            'name': jload['item_name'],
                            'weight': jload['weight'],
                            'shopee_product_status': jload['item_status'],
                            'sequence': sequence,
                        }
                        print(vals_product)
                        if data_ready:
                            print('update')
                            datas.write(vals_product)
                        else:
                            print('create')
                            datas.create(vals_product)

    def post_upload_image(self):
        for rec in self:
            timest = int(time.time())
            host = rec.url_api
            path = "/api/v2/media_space/upload_image"
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            itemstatus = "%5B%22NORMAL%22%5D"
            url = host + path + "?access_token=%s&partner_id=%s&timestamp=%s&sign=%s" % (
            access_token, partner_id, timest, sign)
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&offset=0&page_size=10&item_status=NORMAL&offset=0&page_size=10&update_time_from=1611311600&update_time_to=1611311631" % (access_token,partner_id,shop_id, timest, sign)

            # url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get?partner_id=1023577&sign=%s&timestamp=%s" % (
            # sign, timest)

            attachmentts = self.env['ir.attachment'].search([('name', '=', 'test.png')])
            params_file = []
            for attachmentt in attachmentts:
                filepath = attachmentt._full_path(attachmentt.store_fname)
                file_attach = ('image', ('image', open(filepath, "rb"), 'application/octet-stream'))
                # file_attach = ('file', ('image', open(filepath, "rb"), attachmentt.mimetype))
                # file_attach = ('file', (attachmentt.datas_fname, open(filepath, "rb"), attachmentt.mimetype))
                params_file.append(file_attach)
            # response = requests.post(
            #     url=('%s/other/v1/setSalesOrderCompletewithFiles' % (company_ldap.forca_ws.strip())), headers={
            #         'Forca-Token': self.env.user.forca_token
            #     }, data=params_txt, files=params_file)

            print(url)
            files = [
                ('image',
                 ('image', open('/media/oem/zuku/Addon/HRMS14/shopee/test.png', 'rb'), 'application/octet-stream'))
                # Replace with actual file path
            ]

            payload = json.dumps({
                "scene": "-",
                "image": "path/to/file"
            })
            headers = {
                'Content-Type': 'application/json'
            }
            # response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            response = requests.request("POST", url, headers=headers, data=payload, files=params_file,
                                        allow_redirects=False)

            print(response.text)
            json_loads = json.loads(response.text)

            # rec.access_token_shopee = json_loads['access_token']
            return2 = []
            datas = self.env['product.template']
            try:
                if json_loads:
                    if json_loads['error'] == 'error_param':
                        return2.append(str(json_loads['msg']))
                    else:
                        for jloads in json_loads['response']:
                            for jload in jloads['item_list']:
                                print(jload)
                                data_ready = datas.search([('shopee_product_id', '=', str(jload['item_id']))])
                                # category_id = False
                                # if jload['category_id']:
                                #     category_id = self.env['product.category'].search([('shopee_category_id', '=', jload['category_id'])]).id
                                # vals_product = {
                                #     'shopee_product_id': jload['item_id'],
                                #     'category_id': category_id,
                                #     'name': jload['item_name'],
                                # }
                                # if data_ready:
                                #     updated = datas.write(vals_product)
                                # else:
                                #     created = datas.create(vals_product)
            except Exception as e:
                return2.append(str(e))

    def get_order(self):
        for rec in self:
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

    def get_order_time(self, start_date, end_date):
        for rec in self:
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
            add_fields = "&response_optional_fields=%5Brecipient_address%2Citem_list%2Cbuyer_username%2Cestimated_shipping_fee%2Cpayment_method%2Cshipping_carrier%2Cnote%2Cbuyer_id%2Cpayment_method%5D"
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
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['message']))
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
                            product_ready = self.env['product.product'].search([('shopee_product_id', '=', str(prod['item_id']))], limit=1)
                            if product_ready:
                                vals_item = {
                                    'product_id': product_ready.id,
                                    'name': product_ready.name + ' (model: '+ str(prod['model_name']) + ')',
                                    'product_uom_qty': prod['model_quantity_purchased'],
                                    # 'product_qty': jload['model_quantity_purchased'],
                                    'price_unit': prod['model_original_price']
                                }
                                item_list.append(vals_item)
                                print('-----')
                                print(vals_item)

                        vals_order = {
                            'partner_id': partner.id,
                            'client_order_ref': jload['order_sn'],
                            'note': jload['note'],
                            'shopee_recipient_address': recipient,
                            'shopee_buyer_username' : jload['buyer_username'],
                            'shopee_buyer_id': jload['buyer_id'],
                            'shopee_message_to_seller': jload['message_to_seller'],
                            'shopee_order_status': jload['order_status'],
                            'shopee_payment_method': jload['payment_method'],
                            'shopee_shipping_carrier': jload['shipping_carrier'],
                        }

                        print(vals_order)
                        if data_ready:
                            print('update')
                            updated = data_ready.write(vals_order)
                            ada_data = True
                            for prod in jload['item_list']:
                                product_ready = self.env['product.product'].search([('shopee_product_id', '=', str(prod['item_id']))], limit=1)
                                if product_ready:
                                    vals_item = {
                                        'product_id': product_ready.id,
                                        'name': product_ready.name + ' (model: '+ str(prod['model_name']) + ')',
                                        'product_uom_qty': prod['model_quantity_purchased'],
                                        'price_unit': prod['model_original_price'],
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
                            if data_ready.state == 'draft':
                                updated.action_confirm()
                        else:
                            created = datas.create(vals_order)
                            for prod in jload['item_list']:
                                product_ready = self.env['product.product'].search([('shopee_product_id', '=', str(prod['item_id']))], limit=1)
                                if product_ready:
                                    item_ready = False
                                    vals_item = {
                                        'product_id': product_ready.id,
                                        'name': product_ready.name + ' (model: '+ str(prod['model_name']) + ')',
                                        'product_uom_qty': prod['model_quantity_purchased'],
                                        'price_unit': prod['model_original_price'],
                                        'order_id': created.id
                                    }
                                    for line in data_ready.order_line:
                                        if line.product_id.shopee_product_id == str(prod['item_id']):
                                            wr = line.write(vals_item)
                                            item_ready = True
                                    if not item_ready:
                                        create_line = self.env['sale.order.line'].create(vals_item)
                                else:
                                    updated = created.write({'note': 'produk belum tersikronisasi'})
                            created.action_confirm()


                    # if not ada_data:
                    #     print('jload kosong')
                    #     conf_obj = self.env['ir.config_parameter']
                    #     url_address = False
                    #     forca_address = conf_obj.search([('key', '=', 'shopee.product.id.tes')])
                    #     for con1 in forca_address:
                    #         shopee_item_id = con1.value
                    #     product_ready = False
                    #     data_ready = datas.search([('client_order_ref', '=', order_sn)])
                    #     print(order_sn)
                    #     print(data_ready)
                    #     partner = self.env['res.partner'].search([('name', '=', 'Shopee')], limit=1)
                    #     shipping_address = ''
                    #     item_list = []
                    #     vals_item = False
                    #     product_ready = self.env['product.product'].search([('shopee_product_id', '=', shopee_item_id)], limit=1)
                    #     if product_ready:
                    #         vals_item = {
                    #             'product_id': product_ready.id,
                    #             'name': product_ready.name ,
                    #             'product_uom_qty': 10,
                    #             # 'product_qty': jload['model_quantity_purchased'],
                    #             'price_unit': 12000
                    #         }
                    #         item_list.append(vals_item)
					#
                    #     if partner:
                    #         vals_order = {
                    #             'partner_id': partner.id,
                    #             'client_order_ref': order_sn,
                    #             'note': 'tessss',
                    #         }
                    #     if data_ready:
                    #         vals_order = {
                    #             'partner_id': partner.id,
                    #             'client_order_ref': order_sn,
                    #             'note': 'updateeeee',
                    #         }
                    #         print('update')
                    #         print(vals_order)
                    #         updated = data_ready.write(vals_order)
                    #         for line in data_ready.order_line:
                    #             ada_line = False
                    #             product_ready = self.env['product.product'].search([('shopee_product_id', '=', shopee_item_id)], limit=1)
                    #             vals_item = {
                    #                 'product_id': product_ready.id,
                    #                 'name': product_ready.name,
                    #                 'product_uom_qty': 10,
                    #                 # 'product_qty': jload['model_quantity_purchased'],
                    #                 'price_unit': 10000,
                    #                 'order_id': data_ready.id
                    #             }
                    #             if line.product_id.shopee_product_id == int(shopee_item_id):
                    #                 wr = line.write(vals_item)
                    #                 ada_line = True
					#
                    #     else:
                    #         print('create')
                    #         print(vals_order)
                    #         created = datas.create(vals_order)
                    #         product_ready = self.env['product.product'].search([('shopee_product_id', '=', shopee_item_id)],limit=1)
                    #         if product_ready:
                    #             vals_item = {
                    #                 'product_id': product_ready.id,
                    #                 'name': product_ready.name,
                    #                 'product_uom_qty': 10,
                    #                 # 'product_qty': jload['model_quantity_purchased'],
                    #                 'price_unit': 12000,
                    #                 'order_id': created.id
                    #             }
                    #             create_line = self.env['sale.order.line'].create(vals_item)


    def get_logistic(self):
        for rec in self:
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
                    return2.append(str(json_loads['message']))
                else:
                    for jload in json_loads['response']['logistics_channel_list']:
                        # print(jload)
                        data_ready = datas.search([('shopee_logistic_id', '=', jload['logistics_channel_id'])])

                        vals_logistic = {
                            'name': jload['logistics_channel_name'],
                            'desc': jload['logistics_description'],
                            'enable': jload['enabled'],
                            'shopee_logistic_id': jload['logistics_channel_id'],
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
            # self.get_category()
            self.get_logistic()
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


    def addProduct(self):
        conf_obj = self.env['ir.config_parameter']
        url_address = False
        forca_address = conf_obj.search([('key', '=', 'shopee.address')])
        for con1 in forca_address:
            url_address = con1.value
        forca_token = conf_obj.search([('key', '=', 'shopee.default.token')])
        for rec in self:
            timest = int(time.time())
            host = rec.url_api
            path = "/api/v2/product/add_item"
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
            payload = {
                "description":"Test add item ",
                "item_name":"Hello Add item",
                "category_id":14695,
                "brand":{
                    "brand_id":123,
                    "original_brand_name":"nike"
                },
                "logistic_info":[
                    {
                        "sizeid":0,
                        "shipping_fee":23.12,
                        "enabled":'true',
                        "is_free":'false',
                        "logistic_id":80101
                    },
                    {
                        "shipping_fee":20000,
                        "enabled":'true',
                        "is_free":'false',
                        "logistic_id":80106
                    },
                    {
                        "is_free":'false',
                        "enabled":'false',
                        "logistic_id":86668
                    },
                    {
                        "enabled":'true',
                        "price":12000,
                        "is_free":'true',
                        "logistic_id":88001
                    },
                    {
                        "enabled":'false',
                        "price":2,
                        "is_free":'false',
                        "logistic_id":88014
                    }
                ],
                "weight":1.1,
                "item_status":"UNLIST",
                "image":{
                    "image_id_list":[
                        "a17bb867ecfe900e92e460c57b892590",
                        "30aa47695d1afb99e296956699f67be6",
                        "2ffd521a59da66f9489fa41b5824bb62"
                    ]
                },
                "dimension":{
                    "package_height":11,
                    "package_length":11,
                    "package_width":11
                },
                "attribute_list":[
                    {
                        "attribute_id":4811,
                        "attribute_value_list":[
                            {
                                "value_id":0,
                                "original_value_name":"",
                                "value_unit":""
                            }
                        ]
                    }
                ],
                "original_price":123.3,
                "seller_stock": [
                    {
                        "stock": 0
                    }
                ],
                "tax_info":{
                    "ncm":"123",
                    "same_state_cfop":"123",
                    "diff_state_cfop":"123",
                    "csosn":"123",
                    "origin":"1",
                    "cest":"12345",
                    "measure_unit":"1"
                },
                "complaint_policy":{
                    "warranty_time":"ONE_YEAR",
                    "exclude_entrepreneur_warranty":"123",
                    "diff_state_cfop":'true',
                    "complaint_address_id":123456,
                    "additional_information":""
                },
                "description_type":"extended",
                "description_info":{
                    "extended_description":{
                        "field_list":[
                            {
                                "field_type":"text",
                                "text":"text description 1"
                            },
                            {
                                "field_type":"image",
                                "image_info":{
                                    "image_id":"1e076dff0699d8e778c06dd6c02df1fe"
                                }
                            },
                            {
                                "field_type":"image",
                                "image_info":{
                                    "image_id":"c07ac95ba7bb624d731e37fe2f0349de"
                                }
                            },
                            {
                                "field_type":"text",
                                "text":"text description 1"
                            }
                        ]
                    }
                }
            }

            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            if '404' in str(response.text):
                raise AccessError(_('404 api url not found'))
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['product.template']
            if json_loads:
                if json_loads['codestatus'] == 'E':
                    return2.append(str(json_loads['message']))
                else:
                    for jloads in json_loads['response']:
                            data_ready = datas.search([('shopee_product_id', '=', str(jload['item_id']))])
                            category_id = False
                            if jload['category_id']:
                                category_id = self.env['shopee.product.category'].search([('shopee_category_id', '=', jload['category_id'])]).id
                            vals_product = {
                                'shopee_product_id': str(jload['item_id']),
                                'category_id': category_id,
                                'name': jload['item_name']
                                }
                            if data_ready:
                                updated = datas.write(vals_product)
                            else:
                                created = datas.create(vals_product)
