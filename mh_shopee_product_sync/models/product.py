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



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_shopee= fields.Boolean('Shopee')
    shopee_name = fields.Char('Shopee Name')
    shopee_desc = fields.Char('Shopee Description')
    shopee_product_id = fields.Integer('Shopee Product ID')
    shopee_category_id = fields.Many2one('shopee.product.category','Shopee Category')
    shopee_brand_id = fields.Many2one('shopee.brand','Shopee Brand')

    shopee_price = fields.Float('Shopee Price',digits='Product Price')
    shopee_condition = fields.Selection([('NEW','NEW'),('SECOND','SECOND')], 'Condition')

    shopee_weight = fields.Float("Shopee Weight")
    shopee_length = fields.Float("Shopee Length")
    shopee_width = fields.Float("Shopee Width")
    shopee_height = fields.Float("Shopee Height")

    shopee_sku = fields.Char('SKU')



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

            token2 = "?access_token=" + access_token + "&item_id_list="+ item_list +"&need_complaint_policy=true&need_tax_info=true&partner_id=" + partner_id + "&shop_id=" + shop_id + "&sign=" + sign + "&timestamp=" + timestamp
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
                                category_id = self.env['product.category'].search([('shopee_category_id', '=', jload['category_id'])]).id
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
                "description":"fewajidfosa jioajfiodsa fewajfioewa jicoxjsi fjdiao fjeiwao fdsjiao fejwiao jfdsioafjeiowa jfidsax",
                "item_name":"Hello WXwhGUCI574UsyBHu5J2indlBT6s08av",
                "category_id":14695,
                "brand":{
                    "brand_id":123,
                    "original_brand_name":"nike"
                },
                "logistic_info":[
                    {
                        "sizeid":0,
                        "shipping_fee":23.12,
                        "enabled":true,
                        "is_free":false,
                        "logistic_id":80101
                    },
                    {
                        "shipping_fee":20000,
                        "enabled":true,
                        "is_free":false,
                        "logistic_id":80106
                    },
                    {
                        "is_free":false,
                        "enabled":false,
                        "logistic_id":86668
                    },
                    {
                        "enabled":true,
                        "price":12000,
                        "is_free":true,
                        "logistic_id":88001
                    },
                    {
                        "enabled":false,
                        "price":2,
                        "is_free":false,
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
                    "diff_state_cfop":true,
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
                "description":"fewajidfosa jioajfiodsa fewajfioewa jicoxjsi fjdiao fjeiwao fdsjiao fejwiao jfdsioafjeiowa jfidsax",
                "item_name":"Hello WXwhGUCI574UsyBHu5J2indlBT6s08av",
                "category_id":14695,
                "brand":{
                    "brand_id":123,
                    "original_brand_name":"nike"
                },
                "logistic_info":[
                    {
                        "sizeid":0,
                        "shipping_fee":23.12,
                        "enabled":true,
                        "is_free":false,
                        "logistic_id":80101
                    },
                    {
                        "shipping_fee":20000,
                        "enabled":true,
                        "is_free":false,
                        "logistic_id":80106
                    },
                    {
                        "is_free":false,
                        "enabled":false,
                        "logistic_id":86668
                    },
                    {
                        "enabled":true,
                        "price":12000,
                        "is_free":true,
                        "logistic_id":88001
                    },
                    {
                        "enabled":false,
                        "price":2,
                        "is_free":false,
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
                    "diff_state_cfop":true,
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
