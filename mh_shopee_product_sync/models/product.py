# -*- coding: utf-8 -*-

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
import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource
from odoo.tools import formatLang

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


class ProductProduct(models.Model):
    _inherit = 'product.product'

    shopee_model_id = fields.Char('Shopee Model ID')

    def post_upload_image(self, image, account, productid):
        for rec in self:
            timest = int(time.time())
            host = account.url_api
            path = "/api/v2/media_space/upload_image"
            partner_id = account.partner_id_shopee
            shop_id = account.shop_id_shopee
            access_token = account.access_token_shopee
            tmp = account.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s" % (partner_id, path, timest)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (
                partner_id, timest, sign)
            # print(image)
            print("====================")

            params_file = []
            attachmentts = self.env['ir.attachment'].search(
                [('res_model', '=', 'product.template'), ('res_field', '=', 'image_1920'), ('res_id', '=', productid)])
            params_file = []
            for attachmentt in attachmentts:
                filepath = attachmentt._full_path(attachmentt.store_fname)
                print(filepath)
                file_attach = ('image', ('image', open(filepath, "rb"), 'application/octet-stream'))
                # file_attach = ('file', ('image', open(filepath, "rb"), attachmentt.mimetype))
                # file_attach = ('file', (attachmentt.datas_fname, open(filepath, "rb"), attachmentt.mimetype))
                params_file.append(file_attach)
            # response = requests.post(
            #     url=('%s/other/v1/setSalesOrderCompletewithFiles' % (company_ldap.forca_ws.strip())), headers={
            #         'Forca-Token': self.env.user.forca_token
            #     }, data=params_txt, files=params_file)

            # print(params_file)
            # print(url)
            # files = [
            #     ('image',
            #      ('image', open("/home/meyrina/Pictures/tesshopee.png", "rb"), "application/octet-stream"))
            #     # Replace with actual file path
            # ]

            payload = {}

            # files2 = json.dumps({
            #     files
            # })
            headers = {
            }
            # response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            response = requests.request("POST", url, headers=headers, data=payload, files=params_file,
                                        allow_redirects=False)
            print("===========images===========================")
            print(response.text)
            json_loads = json.loads(response.text)

            # rec.access_token_shopee = json_loads['access_token']
            return2 = []
            datas = self.env['product.template']
            try:
                if json_loads:
                    # print(json_loads['response'])
                    # print("responese==========================")
                    # print(json_loads['response']['image_info'])
                    # print("image_info==========================")
                    # print()
                    # print("image_id==========================")
                    if json_loads['error'] == 'error_param':
                        return2.append(str(json_loads['message']))
                    else:
                        return json_loads['response']['image_info']['image_id']
            except Exception as e:
                return2.append(str(e))

    def upload_marketplace_shopee(self):
        for rec in self:
            timest = int(time.time())
            account = rec.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/add_item"
            partner_id = account.partner_id_shopee
            shop_id = account.shop_id_shopee
            access_token = account.access_token_shopee
            tmp = account.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
                access_token, partner_id, shop_id, timest, sign)
            print(url)
            gambar = []
            logistik = []
            gambarid = self.post_upload_image(rec.image_1920, account, rec.product_tmpl_id.id)
            print(gambarid)
            gambar.append(gambarid)
            # gambar.append('sg-11134201-23020-9muyf8m5h1nve2')
            for logti in rec.shopee_logistic_ids:
                valslog = {
                    "enabled": logti.enable,
                    "is_free": logti.free,
                    "logistic_id": logti.logistic_id.shopee_logistic_id

                }
                logistik.append(valslog)
            attribute = []
            if rec.shopee_attributes_ids:
                for attr in rec.shopee_attributes_ids:
                    if attr.attribute_value_str or attr.attribute_value_id or attr.attribute_value_ids:
                        attrib = {
                            "attribute_id": attr.attribute_id.attribute_id,
                            "attribute_value_list": [],

                        }
                        if attr.attribute_id.input_type == 'TEXT_FILED':
                            attrib['attribute_value_list'] = [
                                {
                                    "value_id": 0,
                                    "original_value_name": attr.attribute_value_str,
                                    "value_unit": ""
                                }
                            ]
                        elif attr.attribute_id.input_type in ['COMBO_BOX', 'DROP_DOWN']:
                            attrib['attribute_value_list'] = [
                                {
                                    "value_id": attr.attribute_value_id.id,
                                }
                            ]
                        elif attr.attribute_id.input_type in ['MULTIPLE_SELECT', 'MULTIPLE_SELECT_COMBO_BOX']:
                            value_ids = []
                            for at in attr.attribute_value_ids:
                                value_ids.append({
                                    "value_id": at.value_id,
                                })
                            attrib['attribute_value_list'] = value_ids
                        attribute.append(attrib)
            shopee_weight = 0.0
            if rec.shopee_weight > 0:
                shopee_weight = rec.shopee_weight / 1000
            payload = json.dumps(
                {
                    "description": rec.shopee_desc,
                    "item_name": rec.shopee_name,
                    "category_id": rec.shopee_category_id.shopee_category_id,
                    "brand": {
                        "brand_id": 0,
                        "original_brand_name": "NoBrand"
                    },
                    "dimension": {
                        "package_height": int(rec.shopee_height),
                        "package_length": int(rec.shopee_length),
                        "package_width": int(rec.shopee_width)
                    },
                    "weight": shopee_weight,
                    "logistic_info": logistik,
                    "item_status": rec.shopee_item_status,
                    "image": {
                        "image_id_list": gambar
                    },
                    "attribute_list": attribute,
                    "original_price": rec.shopee_price,
                    "seller_stock": [
                        {
                            "stock": 0
                        }
                    ],
                    # "tax_info": {
                    #     "ncm": "123",
                    #     "same_state_cfop": "123",
                    #     "diff_state_cfop": "123",
                    #     "csosn": "123",
                    #     "origin": "1",
                    #     "cest": "12345",
                    #     "measure_unit": "1"
                    # },
                    # "complaint_policy": {
                    #     "warranty_time": "ONE_YEAR",
                    #     "exclude_entrepreneur_warranty": "123",
                    #     "diff_state_cfop": true,
                    #     "complaint_address_id": 123456,
                    #     "additional_information": ""
                    # },
                    # "description_type": "extended",
                    # "description_info": {
                    #     "extended_description": {
                    #         "field_list": [
                    #             {
                    #                 "field_type": "text",
                    #                 "text": "text description 1"
                    #             },
                    #             {
                    #                 "field_type": "image",
                    #                 "image_info": {
                    #                     "image_id": "1e076dff0699d8e778c06dd6c02df1fe"
                    #                 }
                    #             },
                    #             {
                    #                 "field_type": "image",
                    #                 "image_info": {
                    #                     "image_id": "c07ac95ba7bb624d731e37fe2f0349de"
                    #                 }
                    #             },
                    #             {
                    #                 "field_type": "text",
                    #                 "text": "text description 1"
                    #             }
                    #         ]
                    #     }
                    # }
                }
            )
            print(url)
            print(payload)
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Notification"),

                    'message': 'Upload Product ',
                    # 'type': 'success',
                    'sticky': True,  # True/False will display for few seconds if false
                },
            }

    def remove_marketplace_shopee(self):
        for rec in self:
            timest = int(time.time())
            account = rec.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/delete_item"
            partner_id = account.partner_id_shopee
            shop_id = account.shop_id_shopee
            access_token = account.access_token_shopee
            tmp = account.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
                access_token, partner_id, shop_id, timest, sign)

            payload = json.dumps(
                {
                    "item_id": int(rec.shopee_product_id),

                }
            )
            print(url)
            print(payload)
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)

            rec.shopee_product_id = False

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Notification"),

                    'message': 'Upload Product ',
                    # 'type': 'success',
                    'sticky': True,  # True/False will display for few seconds if false
                },
            }


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_shopee = fields.Boolean('Shopee')
    shopee_name = fields.Char('Shopee Name')
    shopee_desc = fields.Char('Shopee Description')
    shopee_product_id = fields.Char('Shopee Product ID')
    shopee_category_id = fields.Many2one('shopee.product.category', 'Shopee Category',
                                         domain="[('has_children','=',False)]")
    shopee_brand_id = fields.Many2one('shopee.brand', 'Shopee Brand')
    shopee_account_id = fields.Many2one('marketplace.account', 'Shopee Account')

    shopee_brand_id_domain = fields.Char(
        compute="_compute_shopee_brand_id_domain",
        readonly=True,
        store=False,
    )
    shopee_price = fields.Float('Shopee Price', digits='Product Price')
    shopee_condition = fields.Selection([('NEW', 'NEW'), ('SECOND', 'SECOND')], 'Condition')
    shopee_item_status = fields.Selection([('UNLIST', 'UNLIST'), ('NORMAL', 'NORMAL')], 'Status')

    shopee_weight = fields.Float("Shopee Weight")
    shopee_length = fields.Float("Shopee Length")
    shopee_width = fields.Float("Shopee Width")
    shopee_height = fields.Float("Shopee Height")

    shopee_sku = fields.Char('SKU')
    shopee_logistic_ids = fields.One2many('shopee.logistic.product', 'product_tmpl_id', 'Logistic')
    shopee_attributes_ids = fields.One2many('shopee.product.attribute.product', 'product_tmpl_id', 'Attribute')
    shopee_image_ids = fields.One2many('shopee.image.product', 'product_tmpl_id', 'Image')
    shopee_variant_product_ids = fields.One2many('shopee.attribute.variant.product', 'product_tmpl_id', 'Variant')
    shopee_variant_product_detail_ids = fields.One2many('shopee.attribute.variant.detail', 'product_tmpl_id',
                                                        'Variant Detail')

    # shopee_attribute_line_ids = fields.One2many('product.template.attribute.line', 'product_tmpl_id', 'Product Attributes', copy=True)

    def write(self, vals):
        print(vals)
        res = super(ProductTemplate, self).write(vals)
        return res

    @api.depends('shopee_category_id')
    def _compute_shopee_brand_id_domain(self):
        for rec in self:
            if rec.shopee_category_id:
                brand_obj = self.env['shopee.brand']
                brand_ids = brand_obj.search([('categ_id', '=', rec.shopee_category_id.id)])
                # print(categ_products)
                # print("===============================")
                brand_array = []
                for x in brand_ids:
                    brand_array.append(x.id)

                # return {'domain': {'product_id': [('id', 'in', product_array)]}}
                # print(product_array)
                rec.shopee_brand_id_domain = json.dumps(
                    [('id', 'in', brand_array)]
                )
            else:
                # return {'domain': {'product_id': [('id', '=', 0)]}}
                rec.shopee_brand_id_domain = json.dumps(
                    [('id', '=', 0)]
                )

    def post_upload_image(self, image, account, productid):
        for rec in self:
            timest = int(time.time())
            host = account.url_api
            path = "/api/v2/media_space/upload_image"
            partner_id = account.partner_id_shopee
            shop_id = account.shop_id_shopee
            access_token = account.access_token_shopee
            tmp = account.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s" % (partner_id, path, timest)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (
                partner_id, timest, sign)
            print(image)
            print("====================")

            params_file = []
            attachmentts = self.env['ir.attachment'].search(
                [('res_model', '=', 'product.template'), ('res_field', '=', 'image_1920'), ('res_id', '=', productid)])
            params_file = []
            print(attachmentts)
            for attachmentt in attachmentts:
                filepath = attachmentt._full_path(attachmentt.store_fname)
                print(filepath)
                file_attach = ('image', ('image', open(filepath, "rb"), 'application/octet-stream'))
                # file_attach = ('file', ('image', open(filepath, "rb"), attachmentt.mimetype))
                # file_attach = ('file', (attachmentt.datas_fname, open(filepath, "rb"), attachmentt.mimetype))
                params_file.append(file_attach)
            # response = requests.post(
            #     url=('%s/other/v1/setSalesOrderCompletewithFiles' % (company_ldap.forca_ws.strip())), headers={
            #         'Forca-Token': self.env.user.forca_token
            #     }, data=params_txt, files=params_file)

            # print(params_file)
            # print(url)
            # files = [
            #     ('image',
            #      ('image', open("/home/meyrina/Pictures/tesshopee.png", "rb"), "application/octet-stream"))
            #     # Replace with actual file path
            # ]

            payload = {}

            # files2 = json.dumps({
            #     files
            # })
            headers = {
            }
            # response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            response = requests.request("POST", url, headers=headers, data=payload, files=params_file,
                                        allow_redirects=False)
            print("===========images===========================")
            print(response.text)
            json_loads = json.loads(response.text)

            # rec.access_token_shopee = json_loads['access_token']
            return2 = []
            datas = self.env['product.template']
            try:
                if json_loads:
                    # print(json_loads['response'])
                    # print("responese==========================")
                    # print(json_loads['response']['image_info'])
                    # print("image_info==========================")
                    # print()
                    # print("image_id==========================")
                    if json_loads['error'] == 'error_param':
                        return2.append(str(json_loads['message']))
                    else:
                        return json_loads['response']['image_info']['image_id']
            except Exception as e:
                return2.append(str(e))

    def multipost_upload_image(self, account, id_image):
        for rec in self:
            timest = int(time.time())
            host = account.url_api
            path = "/api/v2/media_space/upload_image"
            partner_id = account.partner_id_shopee
            shop_id = account.shop_id_shopee
            access_token = account.access_token_shopee
            tmp = account.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s" % (partner_id, path, timest)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (
                partner_id, timest, sign)

            params_file = []
            attachmentts = self.env['ir.attachment'].search(
                [('res_model', '=', 'shopee.image.product'), ('res_field', '=', 'image_1920'),
                 ('res_id', '=', id_image)])
            params_file = []
            print(attachmentts)
            for attachmentt in attachmentts:
                filepath = attachmentt._full_path(attachmentt.store_fname)
                print(filepath)
                file_attach = ('image', ('image', open(filepath, "rb"), 'application/octet-stream'))
                # file_attach = ('file', ('image', open(filepath, "rb"), attachmentt.mimetype))
                # file_attach = ('file', (attachmentt.datas_fname, open(filepath, "rb"), attachmentt.mimetype))
                params_file.append(file_attach)
            # response = requests.post(
            #     url=('%s/other/v1/setSalesOrderCompletewithFiles' % (company_ldap.forca_ws.strip())), headers={
            #         'Forca-Token': self.env.user.forca_token
            #     }, data=params_txt, files=params_file)

            # print(params_file)
            # print(url)
            # files = [
            #     ('image',
            #      ('image', open("/home/meyrina/Pictures/tesshopee.png", "rb"), "application/octet-stream"))
            #     # Replace with actual file path
            # ]

            payload = {}

            # files2 = json.dumps({
            #     files
            # })
            headers = {
            }
            # response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            response = requests.request("POST", url, headers=headers, data=payload, files=params_file,
                                        allow_redirects=False)
            print("===========images===========================")
            print(response.text)
            json_loads = json.loads(response.text)

            # rec.access_token_shopee = json_loads['access_token']
            return2 = []
            datas = self.env['product.template']
            try:
                if json_loads:
                    # print(json_loads['response'])
                    # print("responese==========================")
                    # print(json_loads['response']['image_info'])
                    # print("image_info==========================")
                    # print()
                    # print("image_id==========================")
                    if json_loads['error'] == 'error_param':
                        return2.append(str(json_loads['message']))
                    else:
                        return json_loads['response']['image_info']['image_id']
            except Exception as e:
                return2.append(str(e))

    def add_model_product(self):
        for rec in self:
            timest = int(time.time())
            account = rec.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/init_tier_variation"
            partner_id = account.partner_id_shopee
            shop_id = account.shop_id_shopee
            access_token = account.access_token_shopee
            tmp = account.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
                access_token, partner_id, shop_id, timest, sign)
            variant_tier=[]
            for tiervariant in rec.shopee_variant_product_ids:
                tierarray=[]
                for tier in tiervariant.shopee_variant_value_detail_ids:
                    restier={
                             "option": tier.value_id.name,
                             # "image": {"image_id": "82becb4830bd2ee90ad6acf8a9dc26d7"}
                    }
                    tierarray.append(restier)
                valstier = {
                            "name": tiervariant.attribute_id.name,
                            "option_list": tierarray
                        }
                variant_tier.append(valstier)
            detailvariant_tier=[]
            for dtiervariant in rec.shopee_variant_product_detail_ids:
                tiersplit=(dtiervariant.tier).split(",")
                tierarr=[]
                for ts in tiersplit:
                    tierarr.append(int(ts))
                valsdetailtier = {
                            "tier_index": tierarr,
                            "original_price": dtiervariant.shopee_price,
                            "seller_stock": [
                                {
                                    "stock": 0
                                }
                            ]

                        }
                detailvariant_tier.append(valsdetailtier)
            payload = json.dumps(
                {
                    "item_id": int(rec.shopee_product_id),
                    "tier_variation": variant_tier,
                    "model": detailvariant_tier
                }
            )
            print(url)
            print(payload)
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['message']))
                else:
                    if json_loads['response']:
                        if json_loads['response']['model']:
                            for m in json_loads['response']['model']:
                                tierindexstring=[]
                                for tierl in m['tier_index']:
                                    tierindexstring.append(str(tierl))
                                strtier = ','.join((tierindexstring))
                                print(m['tier_index'])
                                print(strtier)
                                variant_ids = self.env['shopee.attribute.variant.detail'].search(
                                    [('tier', '=', strtier)])
                                print(variant_ids)
                                if variant_ids:
                                    variant_ids.product_id.shopee_model_id=m['model_id']
                                    variant_ids.model_id=m['model_id']

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Notification"),

                    'message': 'Upload Product ',
                    # 'type': 'success',
                    'sticky': True,  # True/False will display for few seconds if false
                },
            }

    def upload_marketplace_shopee_create(self):
        for rec in self:
            timest = int(time.time())
            account = rec.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/add_item"
            partner_id = account.partner_id_shopee
            shop_id = account.shop_id_shopee
            access_token = account.access_token_shopee
            tmp = account.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
                access_token, partner_id, shop_id, timest, sign)
            print(url)
            gambar = []
            logistik = []
            gambarid = self.post_upload_image(rec.image_1920, account, rec.id)
            for img in rec.shopee_image_ids:
                gambarid2 = self.multipost_upload_image(account, img.id)
                gambar.append(gambarid2)

            print(gambarid)
            gambar.append(gambarid)
            # gambar.append('sg-11134201-23020-9muyf8m5h1nve2')
            for logti in rec.shopee_logistic_ids:
                valslog = {
                    "enabled": logti.enable,
                    "is_free": logti.free,
                    "logistic_id": logti.logistic_id.shopee_logistic_id

                }
                logistik.append(valslog)
            attribute = []
            if rec.shopee_attributes_ids:
                for attr in rec.shopee_attributes_ids:
                    if attr.attribute_value_str or attr.attribute_value_id or attr.attribute_value_ids:
                        attrib = {
                            "attribute_id": attr.attribute_id.attribute_id,
                            "attribute_value_list": [],

                        }
                        if attr.attribute_id.input_type == 'TEXT_FILED':
                            attrib['attribute_value_list'] = [
                                {
                                    "value_id": 0,
                                    "original_value_name": attr.attribute_value_str,
                                    "value_unit": ""
                                }
                            ]
                        elif attr.attribute_id.input_type in ['COMBO_BOX', 'DROP_DOWN']:
                            attrib['attribute_value_list'] = [
                                {
                                    "value_id": attr.attribute_value_id.id,
                                }
                            ]
                        elif attr.attribute_id.input_type in ['MULTIPLE_SELECT', 'MULTIPLE_SELECT_COMBO_BOX']:
                            value_ids = []
                            for at in attr.attribute_value_ids:
                                value_ids.append({
                                    "value_id": at.value_id,
                                })
                            attrib['attribute_value_list'] = value_ids
                        attribute.append(attrib)
            shopee_weight = 0.0
            if rec.shopee_weight > 0:
                shopee_weight = rec.shopee_weight / 1000
            payload = json.dumps(
                {
                    "description": rec.shopee_desc,
                    "item_name": rec.shopee_name,
                    "category_id": rec.shopee_category_id.shopee_category_id,
                    "brand": {
                        "brand_id": 0,
                        "original_brand_name": "NoBrand"
                    },
                    "dimension": {
                        "package_height": int(rec.shopee_height),
                        "package_length": int(rec.shopee_length),
                        "package_width": int(rec.shopee_width)
                    },
                    "weight": shopee_weight,
                    "logistic_info": logistik,
                    "item_status": rec.shopee_item_status,
                    "image": {
                        "image_id_list": gambar
                    },
                    "attribute_list": attribute,
                    "original_price": rec.shopee_price,
                    "seller_stock": [
                        {
                            "stock": 0
                        }
                    ],

                }
            )
            print(url)
            print(payload)
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['message']))
                else:
                    if json_loads['response']:
                        if json_loads['response']['item_id']:
                            rec.shopee_product_id = json_loads['response']['item_id']
                            self.add_model_product()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Notification"),

                    'message': 'Upload Product ',
                    # 'type': 'success',
                    'sticky': True,  # True/False will display for few seconds if false
                },
            }

    def upload_marketplace_shopee_update(self):
        for rec in self:
            timest = int(time.time())
            account = rec.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/update_item"
            partner_id = account.partner_id_shopee
            shop_id = account.shop_id_shopee
            access_token = account.access_token_shopee
            tmp = account.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
                access_token, partner_id, shop_id, timest, sign)
            print(url)
            gambar = []
            logistik = []
            gambarid = self.post_upload_image(rec.image_1920, account, rec.id)
            print(gambarid)
            gambar.append(gambarid)
            for img in rec.shopee_image_ids:
                gambarid2 = self.multipost_upload_image(account, img.id)
                gambar.append(gambarid2)


            # gambar.append('sg-11134201-23020-9muyf8m5h1nve2')
            for logti in rec.shopee_logistic_ids:
                valslog = {
                    "enabled": logti.enable,
                    "is_free": logti.free,
                    "logistic_id": logti.logistic_id.shopee_logistic_id

                }
                logistik.append(valslog)
            attribute = []
            if rec.shopee_attributes_ids:
                for attr in rec.shopee_attributes_ids:
                    if attr.attribute_value_str or attr.attribute_value_id or attr.attribute_value_ids:
                        attrib = {
                            "attribute_id": attr.attribute_id.attribute_id,
                            "attribute_value_list": [],

                        }
                        if attr.attribute_id.input_type == 'TEXT_FILED':
                            attrib['attribute_value_list'] = [
                                {
                                    "value_id": 0,
                                    "original_value_name": attr.attribute_value_str,
                                    "value_unit": ""
                                }
                            ]
                        elif attr.attribute_id.input_type in ['COMBO_BOX', 'DROP_DOWN']:
                            attrib['attribute_value_list'] = [
                                {
                                    "value_id": attr.attribute_value_id.id,
                                }
                            ]
                        elif attr.attribute_id.input_type in ['MULTIPLE_SELECT', 'MULTIPLE_SELECT_COMBO_BOX']:
                            value_ids = []
                            for at in attr.attribute_value_ids:
                                value_ids.append({
                                    "value_id": at.value_id,
                                })
                            attrib['attribute_value_list'] = value_ids
                        attribute.append(attrib)
            shopee_weight = 0.0
            if rec.shopee_weight > 0:
                shopee_weight = rec.shopee_weight / 1000
            payload = json.dumps(
                {
                    "description": rec.shopee_desc,
                    "item_name": rec.shopee_name,
                    "item_id": int(rec.shopee_product_id),
                    "category_id": rec.shopee_category_id.shopee_category_id,
                    "brand": {
                        "brand_id": 0,
                        "original_brand_name": "NoBrand"
                    },
                    "dimension": {
                        "package_height": int(rec.shopee_height),
                        "package_length": int(rec.shopee_length),
                        "package_width": int(rec.shopee_width)
                    },
                    "weight": shopee_weight,
                    "logistic_info": logistik,
                    "item_status": rec.shopee_item_status,
                    "image": {
                        "image_id_list": gambar
                    },
                    "attribute_list": attribute,
                    "original_price": rec.shopee_price,
                    "seller_stock": [
                        {
                            "stock": 0
                        }
                    ],

                }
            )
            print(url)
            print(payload)
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)

            json_loads = json.loads(response.text)
            return2 = []
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['message']))
                else:
                    if json_loads['response']:
                        if json_loads['response']['item_id']:
                            rec.shopee_product_id = json_loads['response']['item_id']
                            if rec.shopee_variant_product_detail_ids:
                                self.add_model_product()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Notification"),

                    'message': 'Upload Product ',
                    # 'type': 'success',
                    'sticky': True,  # True/False will display for few seconds if false
                },
            }

    def upload_marketplace_shopee_remove(self):
        for rec in self:
            timest = int(time.time())
            account = rec.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/delete_item"
            partner_id = account.partner_id_shopee
            shop_id = account.shop_id_shopee
            access_token = account.access_token_shopee
            tmp = account.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
                access_token, partner_id, shop_id, timest, sign)

            payload = json.dumps(
                {
                    "item_id": int(rec.shopee_product_id),

                }
            )
            print(url)
            print(payload)
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)

            rec.shopee_product_id = False

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Notification"),

                    'message': 'Upload Product ',
                    # 'type': 'success',
                    'sticky': True,  # True/False will display for few seconds if false
                },
            }

    def upload_marketplace_shopee(self):
        for rec in self:
            if not rec.shopee_product_id:

                rec.upload_marketplace_shopee_create()
            else:
                rec.upload_marketplace_shopee_update()

    def remove_marketplace_shopee(self):
        for rec in self:
            if rec.shopee_product_id:
                rec.upload_marketplace_shopee_remove()

    def get_attribute(self, shopee_categ_id):
        for rec in self:
            timest = int(time.time())

            # account=self.account
            account = rec.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/get_attributes"
            host = account.url_api
            partner_id = account.partner_id_shopee
            shop_id = account.shop_id_shopee
            access_token = account.access_token_shopee
            tmp = account.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            datapage = 100
            url = host + path + "?access_token=%s&category_id=%s&language=id&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
                access_token, shopee_categ_id.shopee_category_id, partner_id, shop_id, timest, sign)
            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['shopee.product.attribute']
            datasvalue = self.env['shopee.product.attribute.value']
            datasparent = self.env['shopee.product.attribute.value.parent']
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['message']))
                else:
                    if json_loads['response']:
                        for jload in json_loads['response']['attribute_list']:

                            data_ready = datas.search([('attribute_id', '=', jload['attribute_id'])])
                            vals_product_attribute = {
                                'name': jload['original_attribute_name'],
                                'display_attribute_name': jload['display_attribute_name'],
                                'attribute_id': jload['attribute_id'],
                                'is_mandatory': jload['is_mandatory'],
                                'input_validation_type': jload['input_validation_type'],
                                'format_type': jload['format_type'],
                                'input_type': jload['input_type'],
                                'max_input_value_number': jload['max_input_value_number'],
                                'attribute_unit': jload['attribute_unit'],
                            }
                            if jload['input_validation_type'] == 'DATE_TYPE':
                                vals_product_attribute['date_format_type'] = jload['date_format_type']
                            if data_ready:
                                data_ready.write(vals_product_attribute)
                                attributeid = data_ready
                            else:
                                attributeid = datas.create(vals_product_attribute)

                            for jloadattribute in jload['attribute_value_list']:
                                data_readyvalue = datasvalue.search([('attribute_id', '=', attributeid.id),
                                                                     ('value_id', '=', jloadattribute['value_id'])])
                                vals_product_valueattribute = {
                                    'name': jloadattribute['original_value_name'],
                                    'display_value_name': jloadattribute['display_value_name'],
                                    'value_id': jloadattribute['value_id'],
                                    'attribute_id': attributeid.id,

                                }
                                if 'value_unit' in jloadattribute:
                                    vals_product_valueattribute['value_unit'] = jloadattribute['value_unit']
                                if data_readyvalue:
                                    value_id = data_readyvalue.write(vals_product_valueattribute)
                                    value_id = data_readyvalue
                                else:
                                    value_id = datasvalue.create(vals_product_valueattribute)
                                value_id.parent_attribute_list = False
                                if 'parent_attribute_list' in jloadattribute:
                                    for jloadparentattribute in jloadattribute['parent_attribute_list']:
                                        data_readyparentvalue = datasvalue.search(
                                            [('value_id', '=', jloadparentattribute['parent_value_id'])])

                                        data_readyparent = datas.search(
                                            [('attribute_id', '=', jloadparentattribute['parent_attribute_id'])])
                                        print(data_readyparent)
                                        print(data_readyparentvalue)
                                        print("paratetkektak")
                                        if data_readyparentvalue and data_readyparent:
                                            vals_product_parentattribute = {
                                                'shopee_parent_attribute_id': jloadparentattribute[
                                                    'parent_attribute_id'],
                                                'shopee_parent_value_id': jloadparentattribute['parent_value_id'],
                                                'attribute_value_id': value_id.id,
                                                'parent_attribute_value_id': data_readyvalue.id,
                                                'parent_attribute_id': data_readyparent.id,

                                            }

                                            parent_id = datasparent.create(vals_product_parentattribute)

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

    @api.onchange('shopee_category_id')
    def _onchange_compute_shopee_category_idy(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        # print(res_user.has_group('hr.group_hr_user'))
        for rec in self:
            idprod = rec._origin.id
            print(idprod)
        if self.shopee_category_id:
            self.get_attribute(self.shopee_category_id)
            self.shopee_attributes_ids = False
            timest = int(time.time())

            # account=self.account
            account = self.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/get_attributes"
            host = account.url_api
            partner_id = account.partner_id_shopee
            shop_id = account.shop_id_shopee
            access_token = account.access_token_shopee
            tmp = account.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            datapage = 100
            url = host + path + "?access_token=%s&category_id=%s&language=id&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (
                access_token, self.shopee_category_id.shopee_category_id, partner_id, shop_id, timest, sign)
            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['shopee.product.attribute']
            datas2 = self.env['shopee.product.attribute.product']
            if json_loads:
                if json_loads['error'] == 'error_param':
                    return2.append(str(json_loads['msg']))
                else:
                    if json_loads['response']:
                        for jload in json_loads['response']['attribute_list']:

                            nocreate = False
                            for jloadattribute in jload['attribute_value_list']:

                                if 'parent_attribute_list' in jloadattribute:
                                    nocreate = True
                            attributearray = []
                            if not nocreate:
                                data_ready = datas.search([('attribute_id', '=', jload['attribute_id'])])
                                vals_product_attribute = {
                                    'attribute_id': data_ready[0].id,
                                    'is_mandatory': jload['is_mandatory'],
                                    'input_type': jload['input_type'],
                                }
                                print(vals_product_attribute)
                                attributearray.append((0, 0, vals_product_attribute))
                            self.shopee_attributes_ids = attributearray

    def getProduct(self):
        conf_obj = self.env['ir.config_parameter']
        url_address = False
        forca_address = conf_obj.search([('key', '=', 'shopee.address')])
        for con1 in forca_address:
            url_address = con1.value
        forca_token = conf_obj.search([('key', '=', 'shopee.default.token')])
        if url_address:
            partner_id = 'partner_id'
            shop_id = 'shop_id'
            sign = 'sign'
            timestamp = 'timestamp'
            item_list = ''
            token = "?access_token=" + access_token + "&item_status=NORMAL&offset=0&page_size=10&language=id&partner_id=" + partner_id + "&shop_id=" + shop_id + "&sign=" + sign + "&timestamp=" + timestamp
            url = str(url_address) + "/api/v2/product/get_item_list" + token
            payload = {}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['product.template']
            if json_loads:
                if json_loads['codestatus'] == 'E':
                    return2.append(str(json_loads['message']))
                else:
                    for jloads in json_loads['response']:
                        for jload in jloads['item']:
                            if jload['item_id']:
                                item_list = item_list + ',' + jload['item_id']

            token2 = "?access_token=" + access_token + "&item_id_list=" + item_list + "&need_complaint_policy=true&need_tax_info=true&partner_id=" + partner_id + "&shop_id=" + shop_id + "&sign=" + sign + "&timestamp=" + timestamp
            # url = "https://partner.shopeemobile.com/api/v2/product/get_item_list?access_token=access_token&item_status=NORMAL&offset=0&page_size=10&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp&update_time_from=1611311600&update_time_to=1611311631"
            # url = "https://partner.shopeemobile.com/api/v2/product/get_item_base_info?access_token=access_token&item_id_list=34001,34002&need_complaint_policy=true&need_tax_info=true&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
            url2 = str(url_address) + "/api/v2/product/get_item_base_info" + token2
            payload = {}
            headers = {}
            response = requests.request("GET", url2, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['product.template']
            if json_loads:
                if json_loads['codestatus'] == 'E':
                    return2.append(str(json_loads['message']))
                else:
                    for jloads in json_loads['response']:
                        for jload in jloads['item_list']:
                            print(jload)
                            data_ready = datas.search([('shopee_product_id', '=', jload['item_id'])])
                            category_id = False
                            if jload['category_id']:
                                category_id = self.env['product.category'].search(
                                    [('shopee_category_id', '=', jload['category_id'])]).id
                            vals_product = {
                                'shopee_product_id': jload['item_id'],
                                'category_id': category_id,
                                'name': jload['item_name'],
                            }
                            if data_ready:
                                updated = datas.write(vals_product)
                            else:
                                created = datas.create(vals_product)

    def addProduct(self):
        conf_obj = self.env['ir.config_parameter']
        url_address = False
        forca_address = conf_obj.search([('key', '=', 'shopee.address')])
        for con1 in forca_address:
            url_address = con1.value
        forca_token = conf_obj.search([('key', '=', 'shopee.default.token')])
        if url_address:
            partner_id = 'partner_id'
            shop_id = 'shop_id'
            sign = 'sign'
            timestamp = 'timestamp'
            token = "?access_token=" + access_token + "&partner_id=" + partner_id + "&shop_id=" + shop_id + "&sign=" + sign + "&timestamp=" + timestamp
            # url = "https://partner.shopeemobile.com/api/v2/product/get_item_base_info?access_token=access_token&item_id_list=34001,34002&need_complaint_policy=true&need_tax_info=true&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
            url = str(url_address) + "/api/v2/product/add_item" + token
            payload = {
                "description": "fewajidfosa jioajfiodsa fewajfioewa jicoxjsi fjdiao fjeiwao fdsjiao fejwiao jfdsioafjeiowa jfidsax",
                "item_name": "Hello WXwhGUCI574UsyBHu5J2indlBT6s08av",
                "category_id": 14695,
                "brand": {
                    "brand_id": 123,
                    "original_brand_name": "nike"
                },
                "logistic_info": [
                    {
                        "sizeid": 0,
                        "shipping_fee": 23.12,
                        "enabled": true,
                        "is_free": false,
                        "logistic_id": 80101
                    },
                    {
                        "shipping_fee": 20000,
                        "enabled": true,
                        "is_free": false,
                        "logistic_id": 80106
                    },
                    {
                        "is_free": false,
                        "enabled": false,
                        "logistic_id": 86668
                    },
                    {
                        "enabled": true,
                        "price": 12000,
                        "is_free": true,
                        "logistic_id": 88001
                    },
                    {
                        "enabled": false,
                        "price": 2,
                        "is_free": false,
                        "logistic_id": 88014
                    }
                ],
                "weight": 1.1,
                "item_status": "UNLIST",
                "image": {
                    "image_id_list": [
                        "a17bb867ecfe900e92e460c57b892590",
                        "30aa47695d1afb99e296956699f67be6",
                        "2ffd521a59da66f9489fa41b5824bb62"
                    ]
                },
                "dimension": {
                    "package_height": 11,
                    "package_length": 11,
                    "package_width": 11
                },
                "attribute_list": [
                    {
                        "attribute_id": 4811,
                        "attribute_value_list": [
                            {
                                "value_id": 0,
                                "original_value_name": "",
                                "value_unit": ""
                            }
                        ]
                    }
                ],
                "original_price": 123.3,
                "seller_stock": [
                    {
                        "stock": 0
                    }
                ],
                "tax_info": {
                    "ncm": "123",
                    "same_state_cfop": "123",
                    "diff_state_cfop": "123",
                    "csosn": "123",
                    "origin": "1",
                    "cest": "12345",
                    "measure_unit": "1"
                },
                "complaint_policy": {
                    "warranty_time": "ONE_YEAR",
                    "exclude_entrepreneur_warranty": "123",
                    "diff_state_cfop": true,
                    "complaint_address_id": 123456,
                    "additional_information": ""
                },
                "description_type": "extended",
                "description_info": {
                    "extended_description": {
                        "field_list": [
                            {
                                "field_type": "text",
                                "text": "text description 1"
                            },
                            {
                                "field_type": "image",
                                "image_info": {
                                    "image_id": "1e076dff0699d8e778c06dd6c02df1fe"
                                }
                            },
                            {
                                "field_type": "image",
                                "image_info": {
                                    "image_id": "c07ac95ba7bb624d731e37fe2f0349de"
                                }
                            },
                            {
                                "field_type": "text",
                                "text": "text description 1"
                            }
                        ]
                    }
                }
            }
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['product.template']
            if json_loads:
                if json_loads['codestatus'] == 'E':
                    return2.append(str(json_loads['message']))
                else:
                    for jloads in json_loads['response']:
                        data_ready = datas.search([('shopee_product_id', '=', jload['item_id'])])
                        vals_product = {
                            'shopee_product_id': jload['item_id'],
                        }
                        if data_ready:
                            updated = datas.write(vals_product)
                        else:
                            created = datas.create(vals_product)

    def updateProduct(self):
        conf_obj = self.env['ir.config_parameter']
        url_address = False
        forca_address = conf_obj.search([('key', '=', 'shopee.address')])
        for con1 in forca_address:
            url_address = con1.value
        forca_token = conf_obj.search([('key', '=', 'shopee.default.token')])
        if url_address:
            partner_id = 'partner_id'
            shop_id = 'shop_id'
            sign = 'sign'
            timestamp = 'timestamp'
            token = "?access_token=" + access_token + "&partner_id=" + partner_id + "&shop_id=" + shop_id + "&sign=" + sign + "&timestamp=" + timestamp
            # url = "https://partner.shopeemobile.com/api/v2/product/get_item_base_info?access_token=access_token&item_id_list=34001,34002&need_complaint_policy=true&need_tax_info=true&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
            url = str(url_address) + "/api/v2/product/update_item" + token
            payload = {
                "description": "fewajidfosa jioajfiodsa fewajfioewa jicoxjsi fjdiao fjeiwao fdsjiao fejwiao jfdsioafjeiowa jfidsax",
                "item_name": "Hello WXwhGUCI574UsyBHu5J2indlBT6s08av",
                "category_id": 14695,
                "brand": {
                    "brand_id": 123,
                    "original_brand_name": "nike"
                },
                "logistic_info": [
                    {
                        "sizeid": 0,
                        "shipping_fee": 23.12,
                        "enabled": true,
                        "is_free": false,
                        "logistic_id": 80101
                    },
                    {
                        "shipping_fee": 20000,
                        "enabled": true,
                        "is_free": false,
                        "logistic_id": 80106
                    },
                    {
                        "is_free": false,
                        "enabled": false,
                        "logistic_id": 86668
                    },
                    {
                        "enabled": true,
                        "price": 12000,
                        "is_free": true,
                        "logistic_id": 88001
                    },
                    {
                        "enabled": false,
                        "price": 2,
                        "is_free": false,
                        "logistic_id": 88014
                    }
                ],
                "weight": 1.1,
                "item_status": "UNLIST",
                "image": {
                    "image_id_list": [
                        "a17bb867ecfe900e92e460c57b892590",
                        "30aa47695d1afb99e296956699f67be6",
                        "2ffd521a59da66f9489fa41b5824bb62"
                    ]
                },
                "dimension": {
                    "package_height": 11,
                    "package_length": 11,
                    "package_width": 11
                },
                "attribute_list": [
                    {
                        "attribute_id": 4811,
                        "attribute_value_list": [
                            {
                                "value_id": 0,
                                "original_value_name": "",
                                "value_unit": ""
                            }
                        ]
                    }
                ],
                "original_price": 123.3,
                "seller_stock": [
                    {
                        "stock": 0
                    }
                ],
                "tax_info": {
                    "ncm": "123",
                    "same_state_cfop": "123",
                    "diff_state_cfop": "123",
                    "csosn": "123",
                    "origin": "1",
                    "cest": "12345",
                    "measure_unit": "1"
                },
                "complaint_policy": {
                    "warranty_time": "ONE_YEAR",
                    "exclude_entrepreneur_warranty": "123",
                    "diff_state_cfop": true,
                    "complaint_address_id": 123456,
                    "additional_information": ""
                },
                "description_type": "extended",
                "description_info": {
                    "extended_description": {
                        "field_list": [
                            {
                                "field_type": "text",
                                "text": "text description 1"
                            },
                            {
                                "field_type": "image",
                                "image_info": {
                                    "image_id": "1e076dff0699d8e778c06dd6c02df1fe"
                                }
                            },
                            {
                                "field_type": "image",
                                "image_info": {
                                    "image_id": "c07ac95ba7bb624d731e37fe2f0349de"
                                }
                            },
                            {
                                "field_type": "text",
                                "text": "text description 1"
                            }
                        ]
                    }
                }
            }
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['product.template']
            if json_loads:
                if json_loads['codestatus'] == 'E':
                    return2.append(str(json_loads['message']))
                else:
                    for jloads in json_loads['response']:
                        data_ready = datas.search([('shopee_product_id', '=', jload['item_id'])])
                        vals_product = {
                            'shopee_product_id': jload['item_id'],
                        }
                        if data_ready:
                            updated = datas.write(vals_product)
                        else:
                            created = datas.create(vals_product)


class ShopeeImageProduct(models.Model):
    _name = "shopee.image.product"
    _description = "Shopee Image in Product"

    @api.model
    def _default_image(self):
        image_path = get_module_resource('lunch', 'static/img', 'lunch.png')
        return base64.b64encode(open(image_path, 'rb').read())

    product_tmpl_id = fields.Many2one('product.template', index=True, required=True)
    product_id = fields.Many2one('product.product', index=True)
    image_1920 = fields.Image(default=_default_image)
