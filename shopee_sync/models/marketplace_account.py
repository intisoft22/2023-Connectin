from odoo import fields, models, api
import hmac
import json
from datetime import date, datetime, timedelta
import time
import requests
import hashlib
import urllib.request
from odoo import http
import requests


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
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest,access_token,shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            itemstatus="%5B%22NORMAL%22%5D"
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (access_token,partner_id,shop_id, timest, sign)
            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            # print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['product.category']
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['msg']))
                else:
                    for jload in json_loads['response']['category_list']:
                        # print(jload)
                        data_ready = datas.search([('shopee_category_id', '=', jload['category_id'])])
                        parent_ready = datas.search([('shopee_category_id', '=', jload['parent_category_id'])], limit=1)
                        if parent_ready and data_ready:
                            print(parent_ready.name)
                            print(parent_ready.id)
                            vals_product_category = {
                                'name': jload['original_category_name'],
                                'shopee_category_id': jload['category_id'],
                                'parent_category_id': jload['parent_category_id'],
                                'parent_id': parent_ready.id,
                                'display_category_name': jload['display_category_name'],
                                }
                        else:
                            print(jload['parent_category_id'])
                            vals_product_category = {
                                'name': jload['original_category_name'],
                                'shopee_category_id': jload['category_id'],
                                'parent_category_id': jload['parent_category_id'],
                                # 'parent_id': jload['parent_category_id'],
                                'display_category_name': jload['display_category_name'],
                                }
                        if data_ready:
                            print('update')
                            print(vals_product_category)
                            updated = datas.write(vals_product_category)
                        else:
                            created = datas.create(vals_product_category)


    def get_product(self):
        for rec in self:
            timest = int(time.time())
            host = rec.url_api
            path = "/api/v2/logistics/get_channel_list"
            path = "/api/v2/product/get_item_list"
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest,access_token,shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            itemstatus="%5B%22NORMAL%22%5D"
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (access_token,partner_id,shop_id, timest, sign)
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&page_size=10&item_status=%s" % (access_token,partner_id,shop_id, timest, sign,itemstatus)
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&offset=0&page_size=10&item_status=NORMAL&offset=0&page_size=10&update_time_from=1611311600&update_time_to=1611311631" % (access_token,partner_id,shop_id, timest, sign)
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&offset=0&page_size=100&item_status=NORMAL&offset=0&page_size=10" % (access_token,partner_id,shop_id, timest, sign)

            # url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get?partner_id=1023577&sign=%s&timestamp=%s" % (
            # sign, timest)
            print(url)

            payload = json.dumps({

            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            print(response.text)
            json_loads = json.loads(response.text)

            # rec.access_token_shopee = json_loads['access_token']
            return2 = []
            item_list = 'kosong'
            datas = self.env['product.template']
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['message']))
                else:
                    if (json_loads['response']['total_count'] > 0):
                        for jload in json_loads['response']['item']:
                            if jload['item_id']:
                                if item_list == 'kosong':
                                    item_list = str(jload['item_id'])
                                else:
                                    item_list = item_list + ',' + str(jload['item_id'])
                    else:
                        return2.append(str(json_loads['response']['total_count']))
            self.get_product_detail(item_list)
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
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest,access_token,shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()

            url = host + path + "?item_id_list=%s&access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&need_complaint_policy=true&need_tax_info=true" % (item_list,access_token,partner_id,shop_id, timest, sign)
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
            datas = self.env['product.template']
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['msg']))
                else:
                    for jload in json_loads['response']['item_list']:

                        data_ready = datas.search([('shopee_product_id', '=', jload['item_id'])])
                        category_id = False
                        if 'category_id' in jload:
                            category_id = self.env['product.category'].search([('shopee_category_id', '=', jload['category_id'])]).id
                        if category_id is False:
                            category_id = self.env['product.category'].search([('name', '=', 'All')]).id
                        vals_product = {
                            'shopee_product_id': jload['item_id'],
                            'categ_id': category_id,
                            'name': jload['item_name'],
                            'weight': jload['weight'],
                        }
                        if data_ready:
                            updated = datas.write(vals_product)
                        else:
                            created = datas.create(vals_product)
                        print(vals_product)




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
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest,access_token,shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            itemstatus="%5B%22NORMAL%22%5D"
            url = host + path + "?access_token=%s&partner_id=%s&timestamp=%s&sign=%s" % (access_token,partner_id, timest, sign)
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&offset=0&page_size=10&item_status=NORMAL&offset=0&page_size=10&update_time_from=1611311600&update_time_to=1611311631" % (access_token,partner_id,shop_id, timest, sign)

            # url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get?partner_id=1023577&sign=%s&timestamp=%s" % (
            # sign, timest)




            attachmentts = self.env['ir.attachment'].search([('name', '=', 'test.png')])
            params_file = []
            for attachmentt in attachmentts:
                filepath = attachmentt._full_path(attachmentt.store_fname)
                file_attach = ('image',('image',open(filepath, "rb"),'application/octet-stream'))
                # file_attach = ('file', ('image', open(filepath, "rb"), attachmentt.mimetype))
                # file_attach = ('file', (attachmentt.datas_fname, open(filepath, "rb"), attachmentt.mimetype))
                params_file.append(file_attach)
            # response = requests.post(
            #     url=('%s/other/v1/setSalesOrderCompletewithFiles' % (company_ldap.forca_ws.strip())), headers={
            #         'Forca-Token': self.env.user.forca_token
            #     }, data=params_txt, files=params_file)




            print(url)
            files=[
              ('image',('image',open('/media/oem/zuku/Addon/HRMS14/shopee/test.png','rb'),'application/octet-stream')) # Replace with actual file path
            ]

            payload = json.dumps({
                "scene": "-",
                "image": "path/to/file"
            })
            headers = {
                'Content-Type': 'application/json'
            }
            # response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            response = requests.request("POST", url, headers=headers, data=payload, files=params_file, allow_redirects=False)

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
                                data_ready = datas.search([('shopee_product_id', '=', jload['item_id'])])
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
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest,access_token,shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            # time_from = str(int(datetime.timestamp(datetime.now()-timedelta(days=15))))
            # time_to = str(int(datetime.timestamp(datetime.now())))
            time_from = str(int(datetime.timestamp(datetime.now()-timedelta(days=75))))
            time_to = str(int(datetime.timestamp(datetime.now()-timedelta(days=60))))
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&page_size=20&time_from=%s&time_range_field=create_time&time_to=%s" % (access_token,partner_id,shop_id, timest, sign, time_from, time_to)
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
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest,access_token,shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            # time_from = str(int(datetime.timestamp(datetime.now()-timedelta(days=15))))
            # time_to = str(int(datetime.timestamp(datetime.now())))
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&order_sn_list=%s" % (access_token,partner_id,shop_id, timest, sign, order_sn)
            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['sale.order']
            order_sn = 'kosong'
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['message']))
                else:
                    for jload in json_loads['response']['order_list']:
                        print(jload)
                        if order_sn == 'kosong':
                            order_sn = jload['order_sn']
                        product_ready = False
                        data_ready = datas.search([('client_order_ref', '=', jload['category_id'])])
                        costumer = self.env['res.partner'].search(
                            [('name', '=', 'Shopee')], limit=1)
                        for prod in jload['item_list']:
                            prod['item_id']
                            product_ready = self.env['product.template'].search([('shopee_product_id', '=', prod['item_id'])], limit=1)
                        if product_ready and data_ready:
                            print(product_ready.name)
                            print(product_ready.id)
                            vals_order = {
                                'partner_id': costumer,
                                'client_order_ref': jload['order_sn'],
                                'note': product_ready.name,
                            }
                        else:
                            vals_order = {
                                'partner_id': costumer,
                                'client_order_ref': jload['order_sn'],
                                'note': jload['total_amount'],
                                }
                        if data_ready:
                            print('update')
                            print(vals_order)
                            updated = datas.write(vals_order)
                        else:
                            created = datas.create(vals_order)

