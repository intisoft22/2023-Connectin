
import json
import requests
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression



class ShopeeBrand(models.Model):
    _name = "shopee.brand"
    _description = "Shopee Brand"

    name = fields.Char('Name', index=True, required=True)

    shopee_brand_id = fields.Integer('Shopee Category ID')

    categ_id = fields.Many2one('product.category', 'Parent Category', index=True, ondelete='cascade')

