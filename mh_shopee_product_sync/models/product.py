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
    shopee_model_ids = fields.One2many('shopee.model.product', 'product_id', 'Shopee Model IDs')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_shopee = fields.Boolean('Shopee')
    has_model = fields.Boolean('Has Model')
    variant_ok = fields.Boolean('Variant')
    shopee_name = fields.Char('Shopee Name')
    shopee_desc = fields.Text('Shopee Description')
    shopee_product_id = fields.Char('Shopee Product ID', readonly=1,copy=False)
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
    shopee_condition = fields.Selection([('NEW', 'NEW'), ('USED', 'SECOND')], 'Condition')
    shopee_item_status = fields.Selection([('UNLIST', 'ARCHIVE'), ('NORMAL', 'NORMAL')], 'Status', default='NORMAL')

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

    countvariant_shopee = fields.Integer("Count Variant Shopee", compute="_compute_variant_count", store=True)
    countvariant_odoo = fields.Integer("Count Variant Odoo", compute="_compute_variant_count", store=True)
    needgenerate_shopee = fields.Boolean("Need Generate Variant", compute="_compute_variant_count", store=True)
    needreset_shopee = fields.Boolean("Need Reset Variant", compute="_compute_variant_count", store=True)
    needupdate_shopee = fields.Boolean("Need Update Variant")
    changevariant_shopee = fields.Boolean("Change Variant")
    dateupload_shopee = fields.Datetime("Shopee Upload Date")

    # shopee_attribute_line_ids = fields.One2many('product.template.attribute.line', 'product_tmpl_id', 'Product Attributes', copy=True)

    def write(self, vals):
        print(vals)
        res = super(ProductTemplate, self).write(vals)
        return res

    @api.depends('shopee_variant_product_ids', 'attribute_line_ids')
    def _compute_variant_count(self):
        for prd in self:
            prd.countvariant_shopee = len(prd.shopee_variant_product_ids)
            prd.countvariant_odoo = len(prd.attribute_line_ids)
            if prd.countvariant_odoo > prd.countvariant_shopee:
                prd.needgenerate_shopee = True
                prd.needreset_shopee = False
            else:
                prd.needreset_shopee = True
                prd.needgenerate_shopee = False


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
            if json_loads:
                # print(json_loads['response'])
                # print("responese==========================")
                # print(json_loads['response']['image_info'])
                # print("image_info==========================")
                # print()
                # print("image_id==========================")
                if json_loads['error'] != '':

                    raise UserError(_(str(json_loads['message'])))
                    # return2.append()
                else:
                    return json_loads['response']['image_info']['image_id']

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
            if json_loads:
                # print(json_loads['response'])
                # print("responese==========================")
                # print(json_loads['response']['image_info'])
                # print("image_info==========================")
                # print()
                # print("image_id==========================")
                if json_loads['error'] != '':

                    raise UserError(_(str(json_loads['message'])))
                else:
                    return json_loads['response']['image_info']['image_id']

    def add_model_product(self):
        for rec in self:
            timest = int(time.time())
            account = rec.shopee_account_id
            host = account.url_api
            if self.variant_ok and self.dateupload_shopee:
                path = "/api/v2/product/update_tier_variation"
            else:
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
            variant_tier = []
            for tiervariant in rec.shopee_variant_product_ids:
                tierarray = []
                for tier in sorted(tiervariant.shopee_variant_value_detail_ids2, key=lambda b: (b.tier_tobe)):
                    restier = {
                        "option": tier.value_id2.name,
                        # "image": {"image_id": "82becb4830bd2ee90ad6acf8a9dc26d7"}
                    }
                    tierarray.append(restier)
                print(tierarray)
                print("++_+_+__")
                valstier = {
                    "name": tiervariant.attribute_id2.name,
                    "option_list": tierarray
                }
                variant_tier.append(valstier)
            detailvariant_tier = []
            addmodelarray = []
            for dtiervariant in sorted(rec.shopee_variant_product_detail_ids, key=lambda b: (b.tier_tobe)):
                tiersplit = (dtiervariant.tier_tobe).split(",")
                tierarr = []
                for ts in tiersplit:
                    tierarr.append(int(ts))

                if self.variant_ok and self.dateupload_shopee:
                    if dtiervariant.model_id:
                        valsdetailtier = {
                            "tier_index": tierarr,
                            "model_id": dtiervariant.model_id,
                            "original_price": dtiervariant.shopee_price,
                            "seller_stock": [
                                {
                                    "stock": 0
                                }
                            ]

                        }
                        detailvariant_tier.append(valsdetailtier)
                    else:
                        addmodel = {
                            "tier_index": tierarr,
                            "original_price": dtiervariant.shopee_price,
                            "seller_stock": [
                                {
                                    "stock": 0
                                }
                            ]

                        }
                        addmodelarray.append(addmodel)
                else:
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
            for admodel in addmodelarray:
                createmodeljson=self.create_model_product(int(rec.shopee_product_id),admodel['tier_index'],admodel['original_price'])
                if createmodeljson:
                    if createmodeljson['error'] != '':
                        raise UserError(_(str(createmodeljson['message'])))
                    else:
                        if createmodeljson['response']:
                            if createmodeljson['response']['model']:
                                for m in createmodeljson['response']['model']:
                                    tierindexstring = []
                                    for tierl in m['tier_index']:
                                        tierindexstring.append(str(tierl))
                                    strtier = ','.join((tierindexstring))
                                    print(m['tier_index'])
                                    print(strtier)
                                    variant_ids = self.env['shopee.attribute.variant.detail'].search(
                                        [('tier_tobe', '=', strtier),('product_tmpl_id', '=', rec.id)])
                                    print(variant_ids)
                                    print("=============create")
                                    if variant_ids:
                                        variant_ids.product_id.shopee_model_id = m['model_id']
                                        variant_ids.model_id = m['model_id']
                                        variant_ids.tier = strtier
                                        variant_ids.tier_tobe = strtier
                                        vals3 = []
                                        vals3.append((0, 0, {'product_id': variant_ids.product_id.id, 'model_id': m['model_id']}))
                                        variant_ids.product_id.shopee_model_ids = vals3

            if self.variant_ok  and self.dateupload_shopee:

                for dtiervariant in rec.shopee_variant_product_detail_ids:
                    dtiervariant.tier = dtiervariant.tier_tobe
                    dtiervariant.tier_tobe = False
                for tierv in rec.shopee_variant_product_ids:
                    for tierv2 in tierv.shopee_variant_value_detail_ids2:
                        tierv2.tier = tierv2.tier_tobe
            else:

                if json_loads:
                    if json_loads['error'] != '':
                        raise UserError(_(str(json_loads['message'])))
                    else:
                        if json_loads['response']:
                            if json_loads['response']['model']:
                                for m in json_loads['response']['model']:
                                    tierindexstring = []
                                    for tierl in m['tier_index']:
                                        tierindexstring.append(str(tierl))
                                    strtier = ','.join((tierindexstring))
                                    print(m['tier_index'])
                                    print(strtier)
                                    variant_ids = self.env['shopee.attribute.variant.detail'].search(
                                        [('tier_tobe', '=', strtier),('product_tmpl_id', '=', rec.id)])
                                    print(variant_ids)
                                    if variant_ids:
                                        variant_ids.product_id.shopee_model_id = m['model_id']
                                        variant_ids.model_id = m['model_id']
                                        variant_ids.tier =strtier
                                        variant_ids.tier_tobe = False

                                        vals3 = []
                                        vals3.append((0, 0, {'product_id': variant_ids.product_id.id, 'model_id': m['model_id']}))
                                        variant_ids.product_id.shopee_model_ids = vals3

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

    def delete_model_product(self,item_id,model_id):
        for rec in self:
            timest = int(time.time())
            account = rec.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/delete_model"
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
                    "item_id": int(item_id),
                    "model_id": int(model_id)
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
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
                else:
                    return True

    def create_model_product(self,item_id,tier,price):
        for rec in self:
            timest = int(time.time())
            account = rec.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/add_model"
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

            tierarr = []
            for ts in tier:
                tierarr.append(int(ts))
            payload = json.dumps(
                {
                    "item_id": int(item_id),
                    "model_list": [
                        {
                            "tier_index": tierarr,

                            "original_price": price,
                            "seller_stock": [
                                {
                                    "stock": 0
                                }
                            ]
                        }
                    ]
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
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
                else:
                    return json_loads


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
            if not rec.shopee_logistic_ids:
                raise UserError(_('Logistic info should enable at least one'))
            if rec.image_1920:

                gambarid = self.post_upload_image(rec.image_1920, account, rec.id)

                print(gambarid)
                gambar.append(gambarid)
            else:
                raise UserError(_('Please entry image first!'))

            if rec.shopee_image_ids:
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
                                    "value_id": attr.attribute_value_id.value_id,
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
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
                else:
                    if json_loads['response']:
                        if json_loads['response']['item_id']:
                            rec.shopee_product_id = json_loads['response']['item_id']
                            # if rec.shopee_product_id:
                            #     if rec.shopee_variant_product_detail_ids:
                            #         self.add_model_product()
                            #
                            #         rec.needupdate_shopee = False

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
            if rec.image_1920:

                gambarid = self.post_upload_image(rec.image_1920, account, rec.id)

                print(gambarid)
                gambar.append(gambarid)
            else:

                raise UserError(_('Please entry image first!'))
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
                                    "value_id": attr.attribute_value_id.value_id,
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
                    # "seller_stock": [
                    #     {
                    #         "stock": 0
                    #     }
                    # ],

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
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
                else:
                    if json_loads['response']:
                        if json_loads['response']['item_id']:
                            rec.shopee_product_id = json_loads['response']['item_id']
                            # if rec.needupdate_shopee:
                            #     self.add_model_product()
                            #     rec.needupdate_shopee = False
                            #     rec.changevariant_shopee = False
                            #     rec.variant_ok = False
                            #     rec.has_model = True


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

    def update_price(self,itemid,model_id,price):
        for rec in self:
            timest = int(time.time())
            account = rec.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/update_price"
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
                    "item_id": itemid,
                    "price_list": [{
                        "model_id": model_id,
                        "original_price": price
                    }]
                }
            )
            print(url)
            print(payload)
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)

            if json_loads:
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))

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

            if json_loads:
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
            rec.shopee_product_id = False

            for lne in rec.shopee_variant_product_detail_ids:
                lne.tier_tobe = lne.tier
            product_ids = self.env['product.product'].search(
                [('product_tmpl_id', '=', rec.id)])
            for prd in product_ids:
                prd.shopee_product_id=False
                prd.shopee_model_id=False
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
            rec.shopee_account_id.get_token()
            if  not rec.needupdate_shopee and rec.variant_ok:
                raise UserError(_('Please update variant first!'))
            if not rec.shopee_product_id:

                rec.upload_marketplace_shopee_create()
            else:
                rec.upload_marketplace_shopee_update()
            rec.dateupload_shopee=datetime.now()

            # if rec.shopee_variant_product_detail_ids:
            #     rec.variant_ok=True

    def remove_marketplace_shopee(self):
        for rec in self:
            rec.shopee_account_id.get_token()
            if rec.shopee_product_id:
                rec.upload_marketplace_shopee_remove()

    def updateharga_shopee(self):
        for rec in self:
            rec.shopee_account_id.get_token()
            if not rec.shopee_variant_product_detail_ids:
                self.update_price(int(rec.shopee_product_id), 0, rec.shopee_price)
            else:
                for variasi in rec.shopee_variant_product_detail_ids:
                    if variasi.model_id:
                        self.update_price(int(rec.shopee_product_id), int(variasi.model_id), variasi.shopee_price)
    def updatevariant_shopee(self):
        for rec in self:
            rec.shopee_account_id.get_token()
            rec.add_model_product()

    def reset_variant_shopee(self):
        for rec in self:
            rec.shopee_account_id.get_token()
            if rec.shopee_variant_product_detail_ids:
                for dtiervariant in sorted(rec.shopee_variant_product_detail_ids, key=lambda b: (b.tier_tobe)):
                    item_id= dtiervariant.product_tmpl_id.shopee_product_id
                    model_id= dtiervariant.model_id
                    dtiervariant.product_id.shopee_model_id=False
                    self.delete_model_product(item_id,model_id)
                rec.shopee_variant_product_ids = False
                rec.shopee_variant_product_detail_ids = False
            else:

                raise UserError(_('No Variant'))

    def update_variant_shopee_act(self):
        for rec in self:
            detail_variant_lama = []
            detail_variant_baru = []
            detail_variant = []
            for lne in rec.shopee_variant_product_ids:
                tierlama = []
                tierbaru = []
                tier = []
                seq=0

                # for value2 in lne.shopee_variant_value_detail_ids2:
                #     print(value.tier)
                #     print(value.tier_tobe)
                # for value2 in lne.shopee_variant_value_detail_ids2:
                #
                #     value2.tier_tobe=seq
                #     seq+=1
                for value in lne.shopee_variant_value_detail_ids2:
                    print(value.tier)
                    print(value.tier_tobe)
                    tierlama.append(value.tier)
                    tierbaru.append(value.tier_tobe)
                    tier.append(value)
                detail_variant_lama.append(tierlama)
                detail_variant_baru.append(tierbaru)
                detail_variant.append(tier)
            print(detail_variant_lama)
            print(detail_variant_baru)
            if len(detail_variant) > 1:
                for v0 in detail_variant[0]:

                    for v1 in detail_variant[1]:
                        tierlamastr = str(v0.tier) + "," + str(v1.tier)
                        tierbarustr = str(v0.tier_tobe) + "," + str(v1.tier_tobe)

                        detailvariant_ids = self.env['shopee.attribute.variant.detail'].search(
                            [('product_tmpl_id', '=', rec.id), ('tier', '=', tierlamastr)])
                        if detailvariant_ids:
                            detailvariant_ids.tier_tobe = tierbarustr
                        else:

                            vals_shop = [v0.value_id2.id] + [v1.value_id2.id]

                            rec.shopee_variant_product_detail_ids = [
                                (0, 0, {'shopee_price': rec.shopee_price,'tier_tobe': tierbarustr,
                                        'value_ids': [(6, 0, vals_shop)]})]
            else:
                for v0 in detail_variant[0]:
                    tierlamastr = str(v0.tier)
                    tierbarustr = str(v0.tier_tobe)

                    detailvariant_ids = self.env['shopee.attribute.variant.detail'].search(
                        [('product_tmpl_id', '=', rec.id), ('tier', '=', tierlamastr)])
                    if detailvariant_ids:
                        detailvariant_ids.tier_tobe = tierbarustr
                    else:

                        vals_shop = [v0.value_id2.id]

                        rec.shopee_variant_product_detail_ids = [
                            (0, 0, {'shopee_price': rec.shopee_price,
                                    'tier_tobe': tierbarustr,
                                    'value_ids': [(6, 0, vals_shop)]})]

            for lne in rec.shopee_variant_product_detail_ids:
                valuear = []
                for at in lne.value_ids:
                    valuear.append(at.name)

                product_ids = self.env['product.product'].search(
                    [('product_tmpl_id', '=', rec.id)])
                for prd in product_ids:
                    valueprd = []
                    if prd.product_template_attribute_value_ids:
                        for atprd in prd.product_template_attribute_value_ids:
                            valueprd.append(atprd.name)
                        sama = True
                        for x in valueprd:
                            if x not in valuear:
                                sama = False
                        if sama:
                            lne.product_id = prd.id
                if not lne.tier_tobe:
                    lne.unlink()
            rec.needupdate_shopee = True
            rec.changevariant_shopee = False

    def get_attribute(self, shopee_categ_id):
        for rec in self:
            if not rec.shopee_account_id:
                raise UserError(_('Please entry shopee account first!'))
            rec.shopee_account_id.get_token()
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
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
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
                                    'product_category_ids': [(4, shopee_categ_id.id)],

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

    @api.onchange('name')
    def _onchange_name(self):
        self.shopee_name = self.name

    @api.onchange('shopee_category_id')
    def _onchange_compute_shopee_category_idy(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        # print(res_user.has_group('hr.group_hr_user'))
        for rec in self:
            idprod = rec._origin.id
            print(idprod)

        for rec in self:
            if not rec.shopee_category_id:
                rec.shopee_attributes_ids = False
            else:
                self.get_attribute(rec.shopee_category_id)
                rec.shopee_attributes_ids = False
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
                    access_token, rec.shopee_category_id.shopee_category_id, partner_id, shop_id, timest, sign)
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
                    if json_loads['error'] != '':
                        raise UserError(_(str(json_loads['message'])))
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
                                        'attribute_value_domain': json.dumps( [('attribute_id', '=', data_ready[0].id),('product_category_ids', '=', rec.shopee_category_id.id)])
                                    }
                                    print(vals_product_attribute)
                                    attributearray.append((0, 0, vals_product_attribute))
                                rec.shopee_attributes_ids = attributearray

    def set_logistic_product(self,value_ids):
        for rec in self:
            logisticarray = []
            for v in value_ids:
                datas = self.env['shopee.logistic']
                if v['enabled']:
                    data_ready = datas.search([('shopee_logistic_id', '=', v['logistic_id'])])
                    vals_product_attribute = {
                        'logistic_id': data_ready[0].id,
                        'shop_account_id': rec.shopee_account_id.id,
                        'free': v['is_free'],


                    }

                    logisticarray.append((0, 0, vals_product_attribute))
            rec.shopee_logistic_ids = logisticarray


    def set_attribute_product(self,value_ids):
        for rec in self:
            rec.shopee_attributes_ids = False
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
                access_token, rec.shopee_category_id.shopee_category_id, partner_id, shop_id, timest, sign)
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
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
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
                                    'attribute_value_domain': json.dumps([('attribute_id', '=', data_ready[0].id), (
                                    'product_category_ids', '=', rec.shopee_category_id.id)])
                                }
                                print(value_ids)
                                for value in value_ids:
                                    if value['attribute_id'] ==jload['attribute_id']:
                                        print (value['attribute_id'])
                                        print (jload['attribute_id'])
                                        print (jload['input_type'])
                                        if jload['input_type'] in ['COMBO_BOX','DROP_DOWN']:
                                            datas_value= self.env['shopee.product.attribute.value']
                                            print(value['attribute_value_list'][0]['value_id'])
                                            datavalue_ready = datas_value.search([('value_id', '=', value['attribute_value_list'][0]['value_id'])])
                                            if datavalue_ready:
                                                vals_product_attribute['attribute_value_id']=datavalue_ready[0].id
                                            else:
                                                vals_product_valueattribute = {
                                                    'name': value['attribute_value_list'][0]['original_value_name'],
                                                    'display_value_name': value['attribute_value_list'][0]['original_value_name'],
                                                    'value_id': value['attribute_value_list'][0]['value_id'],
                                                    'attribute_id': data_ready[0].id,
                                                    'product_category_ids': [(4, rec.shopee_category_id.id)],

                                                }
                                                if 'value_unit' in value['attribute_value_list'][0]:
                                                    vals_product_valueattribute['value_unit'] = value['attribute_value_list'][0][
                                                        'value_unit']
                                                value_id = datas_value.create(vals_product_valueattribute)
                                                vals_product_attribute['attribute_value_id'] = value_id.id

                                        if jload['input_type'] == 'TEXT_FILED':
                                            vals_product_attribute['attribute_value_str']=value['attribute_value_list'][0]['original_value_name']
                                        if jload['input_type'] in ['MULTIPLE_SELECT','MULTIPLE_SELECT_COMBO_BOX']:
                                            datas_value= self.env['shopee.product.attribute.value']
                                            attrshopee=[]
                                            for vshopee in value['attribute_value_list']:
                                                datavalue_ready = datas_value.search([('attribute_id', '=', data_ready[0].id),('value_id', '=', vshopee['value_id'])])
                                                if datavalue_ready:
                                                    print(vshopee['value_id'])
                                                    for x in datavalue_ready:
                                                        print(x.name)
                                                    attrshopee.append(datavalue_ready.id)
                                                else:
                                                    vals_product_valueattribute = {
                                                        'name': vshopee['original_value_name'],
                                                        'display_value_name': vshopee['original_value_name'],
                                                        'value_id': vshopee['value_id'],
                                                        'attribute_id': data_ready[0].id,
                                                        'product_category_ids': [(4, rec.shopee_category_id.id)],

                                                    }
                                                    if 'value_unit' in vshopee:
                                                        vals_product_valueattribute['value_unit'] = vshopee[
                                                            'value_unit']
                                                    value_id = datas_value.create(vals_product_valueattribute)

                                                    attrshopee.append(value_id.id)
                                            vals_product_attribute['attribute_value_ids']=[(6,0,attrshopee)]
                                print(vals_product_attribute)
                                attributearray.append((0, 0, vals_product_attribute))
                            rec.shopee_attributes_ids = attributearray


    def set_tier_variant_product(self):
        for rec in self:
            timest = int(time.time())

            rec.attribute_line_ids = False
            rec.shopee_variant_product_ids = False
            rec.shopee_variant_product_detail_ids = False
            # account=self.account
            account = rec.shopee_account_id
            host = account.url_api
            path = "/api/v2/product/get_model_list"
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
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&item_id=%s" % (
                access_token, partner_id, shop_id, timest, sign,rec.shopee_product_id)
            print(url)
            payload = json.dumps({})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            # print(response.text)
            json_loads = json.loads(response.text)
            print(json_loads)
            # rec.access_token_shopee = json_loads['access_token']
            return2 = []
            sequence = 100
            datas = self.env['product.template']
            if json_loads:
                if json_loads['error'] != '':
                    raise UserError(_(str(json_loads['message'])))
                else:
                    vals2=[]
                    vals3=[]
                    for tier in json_loads['response']['tier_variation']:
                        product_attribute_odoo = self.env['product.attribute'].search([('name', '=',tier['name'])])
                        values_odoo = []
                        detail_variant = []
                        if product_attribute_odoo:
                            attribute_id_odoo = product_attribute_odoo[0]
                            tiers=0
                            for value in tier['option_list']:
                                attribute_variant_value_odoo = self.env['product.attribute.value'].search(
                                    [('name', '=', value['option']), ('attribute_id', '=', attribute_id_odoo.id)])
                                if attribute_variant_value_odoo:

                                    values_odoo.append(attribute_variant_value_odoo[0].id)
                                    id_value_odoo=attribute_variant_value_odoo[0]
                                else:
                                    id_value_odoo = self.env['product.attribute.value'].create(
                                        {'name': value['option'],
                                         'attribute_id': attribute_id_odoo.id})

                                    values_odoo.append(id_value_odoo.id)
                                detailvariant = (0, 0, {'value_id2': id_value_odoo.id, 'tier': tiers})
                                detail_variant.append(detailvariant)
                                tiers+=1

                        else:
                            attribute_id_odoo = self.env['product.attribute'].create( {'name': tier['name']})
                            tiers=0
                            for value in tier['option_list']:
                                id_value_odoo = self.env['product.attribute.value'].create(
                                    {'name': value['option'],
                                     'attribute_id': attribute_id_odoo.id})

                                values_odoo.append(id_value_odoo.id)
                                detailvariant = (0, 0, {'value_id2': id_value_odoo.id, 'tier': tiers})
                                detail_variant.append(detailvariant)
                                tiers += 1
                        vals2.append(
                            (0, 0, {'attribute_id': attribute_id_odoo.id, 'value_ids': [(6, 0, values_odoo)]}))
                        vals3.append(
                            (0, 0, {'attribute_id2': attribute_id_odoo.id, 'shopee_variant_value_detail_ids2': detail_variant, 'value_ids2': [(6, 0, values_odoo)]}))
                    rec.attribute_line_ids=vals2
                    rec.shopee_variant_product_ids=vals3
                    vals4=[]
                    values_shop_all = []
                    for variant_shop in rec.shopee_variant_product_ids:

                        values_shop = []
                        for value_shop in variant_shop.value_ids2:
                            values_shop.append(value_shop.id)
                        values_shop_all.append(values_shop)

                    for tier in json_loads['response']['model']:
                        tarray=[]
                        for t in tier['tier_index']:
                            tarray.append(str(t))
                        tierstr=','.join(tarray)
                        vals_shop=[]
                        if len(tier['tier_index'])>1:
                            vals_shop = [values_shop_all[0][tier['tier_index'][0]]] + [values_shop_all[1][tier['tier_index'][1]]]
                        else:

                            vals_shop = [values_shop_all[0][tier['tier_index'][0]]]

                        vals4.append((0, 0, {'shopee_price': tier['price_info'][0]['original_price'], 'tier': tierstr,
                                                         'model_id': tier['model_id'],
                                                         'value_ids': [(6, 0, vals_shop)]}))

                    print(vals4)
                    rec.shopee_variant_product_detail_ids=vals4

                    for p in rec.shopee_variant_product_detail_ids:
                        valuear = []
                        for at in p.value_ids:
                            valuear.append(at.name)
                        product_ids = self.env['product.product'].search(
                            [('product_tmpl_id', '=', rec.id)])
                        for prd in product_ids:
                            valueprd = []
                            if prd.product_template_attribute_value_ids:
                                for atprd in prd.product_template_attribute_value_ids:
                                    valueprd.append(atprd.name)
                                sama = True
                                for x in valueprd:
                                    if x not in valuear:
                                        sama = False
                                if sama:
                                    p.product_id = prd.id
                                    p.product_id.shopee_model_id = p.model_id

                                    vals30 = []
                                    vals30.append(
                                        (0, 0, {'product_id': p.product_id.id, 'model_id': p.model_id}))
                                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                                    print(vals30)
                                    p.product_id.shopee_model_ids = vals30
                    # values_shop_all = []
                    # for variant_shop in rec.shopee_variant_product_ids:
                    #
                    #     values_shop = []
                    #     for value_shop in variant_shop.value_ids2:
                    #         values_shop.append(value_shop.id)
                    #     values_shop_all.append(values_shop)
                    # tier1 = 0
                    # tierstr = []
                    # print((values_shop_all))
                    # print(len(values_shop_all))
                    # if len(values_shop_all) > 1:
                    #     for v0 in values_shop_all[0]:
                    #
                    #         tier2 = 0
                    #         for v1 in values_shop_all[1]:
                    #             vals_shop = [v0] + [v1]
                    #             tierstr = str(tier1) + "," + str(tier2)
                    #             tier2 += 1
                    #             vals3.append((0, 0, {'shopee_price': rec.shopee_price, 'tier': tierstr,
                    #                                  'tier_tobe': tierstr,
                    #                                  'value_ids': [(6, 0, vals_shop)]}))
                    #
                    #         tier1 += 1
                    # else:
                    #
                    #     for v0 in values_shop_all[0]:
                    #         vals_shop = [v0]
                    #         tierstr = str(tier1)
                    #         vals3.append(
                    #             (0, 0, {'shopee_price': product_obj.shopee_price, 'tier': tierstr, 'tier_tobe': tierstr,
                    #                     'value_ids': [(6, 0, vals_shop)]}))
                    #
                    #         tier1 += 1
                    #     print(vals3)
                    # print("==================")
                    # product_obj.shopee_variant_product_detail_ids = vals3
                    # for p in rec.shopee_variant_product_detail_ids:
                    #     valuear = []
                    #     for at in p.value_ids:
                    #         valuear.append(at.name)
                    #
                    #     product_ids = self.env['product.product'].search(
                    #         [('product_tmpl_id', '=', self.env.context['active_ids'])])
                    #     for prd in product_ids:
                    #         valueprd = []
                    #         if prd.product_template_attribute_value_ids:
                    #             for atprd in prd.product_template_attribute_value_ids:
                    #                 valueprd.append(atprd.name)
                    #             sama = True
                    #             for x in valueprd:
                    #                 if x not in valuear:
                    #                     sama = False
                    #             if sama:
                    #                 p.product_id = prd.id
                    #
                    # product_obj.needgenerate_shopee = False
                    # product_obj.needupdate_shopee = True
                    # product_obj.changevariant_shopee = False
                    # product_obj.variant_ok = False
                    #

class ShopeeImageProduct(models.Model):
    _name = "shopee.image.product"
    _description = "Shopee Image in Product"

    product_tmpl_id = fields.Many2one('product.template', index=True)
    product_id = fields.Many2one('product.product', index=True)
    image_1920 = fields.Image('Image')
class ShopeeModelProduct(models.Model):
    _name = "shopee.model.product"
    _description = "Shopee Image in Product"

    product_id = fields.Many2one('product.product', index=True)
    model_id = fields.Char('Model Id')