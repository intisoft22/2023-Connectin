# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import xlwt, xlsxwriter
import base64
import time
from datetime import datetime, timedelta, date
from time import strptime
import math


class ShopeeGetOrder(models.TransientModel):
    _name = 'shopee.get.order'
    _description = 'Report KPI Individu'

    def get_default_date_start(self):
        date_now = (datetime.now()-timedelta(days=14))
        return date_now

    def get_default_date_end(self):
        date_now = (datetime.now())
        return date_now

    start_date = fields.Datetime('Start Date', default=get_default_date_start, required=True)
    end_date = fields.Datetime('End Date', default=get_default_date_end, required=True)
    marketplace_account_id = fields.Many2one('marketplace.account', string='Marketplace Account', required=True)

    def get_shopee_order(self):
        for o in self:
            if o.marketplace_account_id:
                acc = self.env['marketplace.account'].search([('id', '=', o.marketplace_account_id.id)], order="name")
                if o.start_date and o.end_date:
                    start_date = str(int(datetime.timestamp(o.start_date)))
                    end_date = str(int(datetime.timestamp(o.end_date)))
                    acc.get_order_time(start_date,end_date)
                    print('get order done')
        return True

