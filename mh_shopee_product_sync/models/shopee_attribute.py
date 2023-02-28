from odoo import fields, models, api

import json
import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta


class ProductAttributeValueParent(models.Model):
    _name = 'shopee.product.attribute.value.parent'

    shopee_parent_attribute_id = fields.Integer('Shopee Parent Attribute Id')
    shopee_parent_value_id = fields.Integer('Shopee Parent Value Id')
    attribute_value_id = fields.Many2one('shopee.product.attribute.value', string='Value Id')
    parent_attribute_value_id = fields.Many2one('shopee.product.attribute.value', string='Value Id')
    parent_attribute_id = fields.Many2one('shopee.product.attribute', string='Value Id')

class ProductAttributeValue(models.Model):
    _name = 'shopee.product.attribute.value'
    _description = "Shopee Product Attribute Value"

    display_value_name = fields.Char('Display Value Name')
    name = fields.Char('Original Attribute Name')
    value_id = fields.Integer('Value Id')
    value_unit = fields.Char('Value Unit')
    parent_attribute_list = fields.One2many('shopee.product.attribute.value.parent', 'attribute_value_id', string="Parent Attribute ID")
    attribute_id = fields.Many2one('shopee.product.attribute', string='Attribute ID')


class ProductAttribute(models.Model):
    _name = 'shopee.product.attribute'
    _description = "Shopee Product Attribute "

    display_attribute_name = fields.Char('Display Attribute Name')
    name = fields.Char('Original Attribute Name')
    attribute_id = fields.Integer('Shopee Attribute Id')
    is_mandatory = fields.Boolean('Mandatory')
    input_validation_type = fields.Char('Input Validate Type')
    format_type = fields.Char('Format Type')
    date_format_type = fields.Char('Date Format Type')
    input_type = fields.Char('Input Type')
    attribute_unit = fields.Char('Attribute Unit')
    max_input_value_number = fields.Integer('Max Input Value Number')
    attribute_value_list = fields.One2many('shopee.product.attribute.value', 'attribute_id', string="attribute_value_list")

    def getAttributes(self):
        conf_obj = self.env['ir.config_parameter']
        access_token = 'access_token'
        url_address = False
        forca_address = conf_obj.search([('key', '=', 'shopee.address')])
        for con1 in forca_address:
            url_address = con1.value
        forca_token = conf_obj.search([('key', '=', 'shopee.default.token')])
        for con1 in forca_token:
            access_token = con1.value
        if url_address:
            # url = str(url_address) + '/api/v2/product/get_category'
            # body = {}
            # response = requests.request("POST", url, headers=header2, data=(body))
            partner_id = 'partner_id'
            shop_id = 'shop_id'
            sign = 'sign'
            timestamp = 'timestamp'
            token = "?access_token="+access_token+"&language=id&partner_id="+partner_id+"&shop_id="+shop_id+"&sign="+sign+"&timestamp="+timestamp
            # url = str(url_address) + "/api/v2/product/get_category?access_token=access_token&language=id&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
            url = str(url_address) + "/api/v2/product/get_attributes" + token
            payload = {}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            print(response.text)
            json_loads = json.loads(response.text)
            return2 = []
            datas = self.env['shopee.product.attribute']
            if json_loads:
                if json_loads['codestatus'] == 'E':
                    return2.append(str(json_loads['message']))
                else:
                    for jloads in json_loads['response']:
                        for jload in jloads['attribute_list']:
                            print(jload)
                            data_ready = datas.search([('attribute_id', '=', jload['attribute_id'])])
                            parentatts = []
                            atts = []
                            for jloadval in jloads['attribute_list']:
                                attribute_value = self.env['shopee.product.attribute.value'].search([('attribute_id', '=', jloadval['value_id'])])
                                for jloadvalpar in jloadval['parent_attribute_list']:
                                    attribute_value = self.env['shopee.product.attribute.value.parent'].search([('parent_attribute_id', '=', jloadvalpar['parent_attribute_id'])])
                                    parentatt = {
                                        'parent_attribute_id': jloadvalpar['parent_attribute_id'],
                                        'parent_value_id': jloadvalpar['parent_value_id'],
                                    }
                                    parentatts.append(parentatt)
                                att = {
                                    'value_id': jloadval['value_id'],
                                    'display_value_name': jloadval['display_value_name'],
                                    'name': jloadval['original_value_name'],
                                    'value_unit': jloadval['value_unit'],
                                    'parent_attribute_list' : parentatts
                                }
                                atts.append(att)
                            vals_product_attribute = {
                                'attribute_id': jload['attribute_id'],
                                'display_attribute_name': jload['display_attribute_name'],
                                'name': jload['original_attribute_name'],
                                'attribute_id': jload['Shopee attribute id'],
                                'is_mandatory': jload['is_mandatory'],
                                'input_validation_type': jload['input_validation_type'],
                                'format_type': jload['format_type'],
                                'date_format_type': jload['date_format_type'],
                                'input_type': jload['input_type'],
                                'attribute_unit': jload['attribute_unit'],
                                'max_input_value_number': jload['max_input_value_number'],
                                'attribute_value_list': att,
                                }
                            if data_ready:
                                updated = datas.write(vals_product_attribute)
                            else:
                                created = datas.create(vals_product_attribute)

class ShopeeProductAttributeProduct(models.Model):
    _name = "shopee.product.attribute.product"
    _description = "Shopee Product Attribute in Product"

    product_tmpl_id = fields.Many2one('product.template', index=True, required=True)
    product_id = fields.Many2one('product.product', index=True)
    attribute_id = fields.Many2one('shopee.product.attribute', index=True, required=True)
    is_mandatory = fields.Boolean('Mandatory')
    input_type = fields.Char('Input Type')
    attribute_value_id = fields.Many2one('shopee.product.attribute.value','Value', index=True, )
    attribute_value_ids = fields.Many2many('shopee.product.attribute.value','attribute_value_product_rel','attribute_product_id','value_id',string='Value', index=True, )
    attribute_value_str = fields.Char('Value')
    attribute_value_display = fields.Char('Value')