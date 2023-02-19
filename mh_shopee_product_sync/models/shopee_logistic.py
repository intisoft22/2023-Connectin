
import json
import requests
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression



class ShopeeLogistic(models.Model):
    _name = "shopee.logistic"
    _description = "Shopee Logistic"

    name = fields.Char('Name', index=True, required=True)
    desc = fields.Text('Desc',  required=True)
    enable = fields.Boolean('Enable',  required=True)
    cod_enabled = fields.Boolean('COD Enable',  required=True)

    shopee_logistic_id = fields.Integer('Shopee Logistic ID')


    fee_type = fields.Char('Fee Type', index=True, required=True)


class ShopeeLogisticProduct(models.Model):
    _name = "shopee.logistic.product"
    _description = "Shopee Logistic in Product"

    product_tmpl_id = fields.Many2one('product.template', index=True, required=True)
    product_id = fields.Many2one('product.product', index=True, required=True)
    logistic_id = fields.Many2one('shopee.logistic', index=True, required=True)
    enable = fields.Boolean('Enable',  required=True)
    free = fields.Boolean('Free',  required=True)

    fee = fields.Float('Shipping Fee', index=True, required=True)
    est_fee = fields.Float('Shipping Fee', index=True, required=True)