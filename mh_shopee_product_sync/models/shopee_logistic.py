
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
    active = fields.Boolean('Enable',  required=True)

    shopee_logistic_id = fields.Integer('Shopee Logistic ID')


