
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
    mask_channel_id = fields.Char('Parent',  required=True)

    shopee_logistic_id = fields.Integer('Shopee Logistic ID')
    shop_account_id = fields.Many2one('marketplace.account', 'Shopee Account')


    fee_type = fields.Char('Fee Type', index=True, required=True)


class ShopeeLogisticProduct(models.Model):
    _name = "shopee.logistic.product"
    _description = "Shopee Logistic in Product"

    product_tmpl_id = fields.Many2one('product.template', index=True)
    product_id = fields.Many2one('product.product', index=True)
    logistic_id = fields.Many2one('shopee.logistic', index=True, required=True)
    enable = fields.Boolean('Enable',  required=True,default=True)
    free = fields.Boolean('Free',  required=True)
    shop_account_id = fields.Many2one('marketplace.account', 'Shopee Account')

    fee = fields.Float('Shipping Fee', index=True,)
    est_fee = fields.Float('Shipping Fee', index=True)
    logistic_domain = fields.Char(
        compute="_compute_logistic_domain",
        readonly=True,
        store=False,
    )

    @api.depends('shop_account_id')
    def _compute_logistic_domain(self):
        for rec in self:
            if rec.shop_account_id:
                logistic_obj = self.env['shopee.logistic']
                logistic_ids = logistic_obj.search([('shop_account_id', '=', rec.shop_account_id.id),('enable', '=', True),('mask_channel_id', '=', 0)])
                # print(categ_products)
                # print("===============================")
                logistic_array = []
                for x in logistic_ids:
                    logistic_array.append(x.id)

                # return {'domain': {'product_id': [('id', 'in', product_array)]}}
                # print(product_array)
                rec.logistic_domain = json.dumps(
                    [('id', 'in', logistic_array)]
                )
            else:
                # return {'domain': {'product_id': [('id', '=', 0)]}}
                rec.logistic_domain = json.dumps(
                    [('id', '=', 0)]
                )