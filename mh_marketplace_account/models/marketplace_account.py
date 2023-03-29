from odoo import fields, models, api
import hmac
import json
import time
import requests
import hashlib
import urllib.request
from odoo import http
import requests
import time
from datetime import datetime, timedelta, date


class MarketplaceAccount(models.Model):
    _name = 'marketplace.account'
    _description = 'Marketplace account'

    name = fields.Char()
    marketplace = fields.Selection(selection=[('shopee', 'Shopee')], string='Marketplace')
    state = fields.Selection(selection=[('new', 'New'), ('authenticated', 'Authenticated')], default='new',
                             string='Status')
    active = fields.Boolean('Active')
    company_id = fields.Many2one('res.company', 'Company')
    partner_id_shopee = fields.Char('Partner ID')
    partner_key_shopee = fields.Char('Partner Key')
    shop_id_shopee = fields.Char('Shop ID')
    code_shopee = fields.Char('Code')
    access_token_shopee = fields.Char('Access Token')
    refresh_access_token_shopee = fields.Char('Refresh Access Token')
    url_auth = fields.Char('URL AUTH')
    url_api = fields.Char('Url')
    api_path = fields.Char('API')
    date_updated = fields.Datetime('Last Get Order')
    expiry_token = fields.Datetime('Token Expiry Date')

    def shop_auth():
        timest = int(time.time())
        host = "https://partner.test-stable.shopeemobile.com"
        path = "/api/v2/shop/auth_partner"
        redirect_url = "https://intisoftware.com/"
        partner_id = 1023577
        tmp = "6f7853506a61647955646b79736e64596b45474e4e7048564f54774d4a5a6a41"
        partner_key = tmp.encode()
        tmp_base_string = "%s%s%s" % (partner_id, path, timest)
        base_string = tmp_base_string.encode()
        sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
        ##generate api
        url = host + path + "?partner_id=%s&timestamp=%s&sign=%s&redirect=%s" % (partner_id, timest, sign, redirect_url)
        print(url)

    def confirm_authenticated(self):
        for rec in self:
            timest = int(time.time())
            host = rec.url_api
            base = self.env['ir.config_parameter'].get_param('web.base.url')
            path = "/api/v2/shop/auth_partner"
            redirect_url = "https://intisoftware.com/"
            partner_id = rec.partner_id_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s" % (partner_id, path, timest)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            ##generate api
            url = host + path + "?partner_id=%s&timestamp=%s&sign=%s&redirect=%s" % (
                partner_id, timest, sign, redirect_url)
            print(url)
            rec.url_auth = url
            rec.access_token_shopee = False
            rec.refresh_access_token_shopee = False
            # html_page = requests.get(url)
            # return html_page
            # webUrl = urllib.request.urlopen(url)

    def set_draft(self):
        for rec in self:
            rec.state='new'

    def check_expiry_token(self):
        for rec in self:

            if datetime.strptime((str(datetime.now()).split('.')[0]), "%Y-%m-%d %H:%M:%S")> datetime.strptime((str(rec.expiry_token).split('.')[0]), "%Y-%m-%d %H:%M:%S"):
                rec.get_token()

    def get_token(self):
        for rec in self:
            timest = int(time.time())
            host = rec.url_api
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            tmp = rec.partner_key_shopee
            if rec.access_token_shopee:
                access_token=rec.access_token_shopee
                refresh_access_token_shopee=rec.refresh_access_token_shopee
                path = "/api/v2/auth/access_token/get"
                partner_key = tmp.encode()
                tmp_base_string = "%s%s%s" % (partner_id, path, timest)
                base_string = tmp_base_string.encode()
                sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()

                url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (partner_id, timest, sign)
                # url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get?partner_id=1023577&sign=%s&timestamp=%s" % (
                # sign, timest)
                print(url)

                payload = json.dumps({
                    "refresh_token":refresh_access_token_shopee,
                    "partner_id": int(partner_id),
                    "shop_id": int(shop_id)
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)

                print(response.text)
                json_loads = json.loads(response.text)
                rec.access_token_shopee = json_loads['access_token']
                rec.refresh_access_token_shopee = json_loads['refresh_token']
                rec.expiry_token=datetime.now()+timedelta(seconds=json_loads['expire_in'])
            else:
                path = "/api/v2/auth/token/get"
                code = rec.code_shopee
                partner_key = tmp.encode()
                tmp_base_string = "%s%s%s" % (partner_id, path, timest)
                base_string = tmp_base_string.encode()
                sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()

                url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (partner_id, timest, sign)
                # url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get?partner_id=1023577&sign=%s&timestamp=%s" % (
                # sign, timest)
                print(url)

                payload = json.dumps({
                    "code": code,
                    "partner_id": int(partner_id),
                    "shop_id": int(shop_id)
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)

                print(response.text)
                json_loads = json.loads(response.text)
                rec.access_token_shopee = json_loads['access_token']
                rec.refresh_access_token_shopee = json_loads['refresh_token']
                rec.expiry_token=datetime.now()+timedelta(seconds=json_loads['expire_in'])
            rec.state='authenticated'

    def get_product(self):
        for rec in self:
            timest = int(time.time())
            host = rec.url_api
            path = "/api/v2/logistics/get_channel_list"
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest,access_token,shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            itemstatus="%5B%22NORMAL%22%5D"
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (access_token,partner_id,shop_id, timest, sign)
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&offset=0&page_size=10&item_status=NORMAL&offset=0&page_size=10&update_time_from=1611311600&update_time_to=1611311631" % (access_token,partner_id,shop_id, timest, sign)

            # url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get?partner_id=1023577&sign=%s&timestamp=%s" % (
            # sign, timest)
            print(url)

            payload = json.dumps({

            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

            print(response.text)
            json_loads = json.loads(response.text)
            # rec.access_token_shopee = json_loads['access_token']

    def get_pathapi(self):
        for rec in self:
            rec.check_expiry_token()
            timest = int(time.time())
            host = rec.url_api
            path = rec.api_path
            partner_id = rec.partner_id_shopee
            shop_id = rec.shop_id_shopee
            access_token = rec.access_token_shopee
            tmp = rec.partner_key_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timest,access_token,shop_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            itemstatus="%5B%22NORMAL%22%5D"
            url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s" % (access_token,partner_id,shop_id, timest, sign)
            # url = host + path + "?access_token=%s&partner_id=%s&shop_id=%s&timestamp=%s&sign=%s&offset=0&page_size=10&item_status=NORMAL&offset=0&page_size=10&update_time_from=1611311600&update_time_to=1611311631" % (access_token,partner_id,shop_id, timest, sign)

            # url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get?partner_id=1023577&sign=%s&timestamp=%s" % (
            # sign, timest)
            print(url)


            # rec.access_token_shopee = json_loads['access_token']
