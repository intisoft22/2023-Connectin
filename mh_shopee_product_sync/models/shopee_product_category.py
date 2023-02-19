# -*- coding: utf-8 -*-

import json
import requests
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression



class ShopeeProductCategory(models.Model):
    _name = "shopee.product.category"
    _description = "Shopee Product Category"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char('Name', index=True, required=True)

    shopee_category_id = fields.Integer('Shopee Category ID')
    has_children = fields.Boolean('has_children')
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)

    parent_category_id = fields.Char('Shopee Parent Category ID')
    parent_id = fields.Many2one('shopee.product.category', 'Shopee Parent Category', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('shopee.product.category', 'parent_id', 'Child Categories')
    product_count = fields.Integer(
        '# Products', compute='_compute_product_count',
        help="The number of products under this category (Does not consider the children categories)")
    display_category_name = fields.Char('Shopee Display Category Name')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    def _compute_product_count(self):
        read_group_res = self.env['product.template'].read_group([('shopee_category_id', 'child_of', self.ids)], ['shopee_category_id'], ['shopee_category_id'])
        group_data = dict((data['shopee_category_id'][0], data['categ_id_count']) for data in read_group_res)
        for categ in self:
            product_count = 0
            for sub_categ_id in categ.search([('id', 'child_of', categ.ids)]).ids:
                product_count += group_data.get(sub_categ_id, 0)
            categ.product_count = product_count

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))
        return True

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

