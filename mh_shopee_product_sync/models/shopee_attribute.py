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
    product_category_ids = fields.Many2many('shopee.product.category', 'attribute_value_product_category_rel',
                                       'product_category_id', 'value_id', string='Product Category',  )


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



class ShopeeProductAttributeProduct(models.Model):
    _name = "shopee.product.attribute.product"
    _description = "Shopee Product Attribute in Product"

    product_tmpl_id = fields.Many2one('product.template')
    product_id = fields.Many2one('product.product', index=True)
    attribute_id = fields.Many2one('shopee.product.attribute',  required=True)
    is_mandatory = fields.Boolean('Mandatory')
    input_type = fields.Char('Input Type')
    attribute_value_id = fields.Many2one('shopee.product.attribute.value',string='Value',)
    attribute_value_ids = fields.Many2many('shopee.product.attribute.value','attribute_value_product_rel','attribute_product_id','value_id',string='Value',  )
    attribute_value_str = fields.Char('Value')
    attribute_value_display = fields.Char('Value',compute='_compute_display_value',store=True)

    attribute_value_domain = fields.Char(
        default="[]"
    )

    @api.onchange('attribute_value_id')
    def _compute_attribute_value_id(self):
        print(self.attribute_value_id.name)

    @api.depends('attribute_value_id','attribute_value_ids','attribute_value_str')
    def _compute_display_value(self):
        print("Tesss============")
        # print(self.attribute_value_id.name)
        for at in self:
            if at.attribute_value_id:
                at.attribute_value_display=at.attribute_value_id.name
            if at.attribute_value_str:
                at.attribute_value_display=at.attribute_value_str
            if at.attribute_value_ids:
                att=[]
                for x in at.attribute_value_ids:
                    att.append(x.name)
                at.attribute_value_display=', '.join(att)
