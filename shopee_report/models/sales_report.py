# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date
import time

def lengthmonth(year, month):
    if month == 2 and ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]


def month2name(month):
    return \
        ['Desember', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober',
         'November', 'Desember'][month]

class SalesReport(models.Model):
    _name = "sales.report"
    _description = "Generate Sales Report"
    _order = 'year desc, month desc'

    def month2name(self, month):
        return [0, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][month]

    marketplace_id = fields.Many2one('marketplace.account', string="Marketplace Account", required=True)

    month = fields.Selection(
        [('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'),
         ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month',
        required=True, default=lambda *a: str(time.gmtime()[1]))

    year = fields.Integer('Year', required=True, default=lambda *a: time.gmtime()[0])

    state = fields.Selection([('draft', 'Draft'), ('on_period', 'On Period'),
                              ('close', 'Close'), ('cancel', 'Cancelled')], default='draft',
                             string="Status", tracking=True)

    line_ids = fields.One2many('sales.report.line', 'sales_report_line_id', string='Sales Order', readonly=True)

    total_expense = fields.Float('Total Expense')
    total_net_sell = fields.Float('Total Net Sell', readonly=True)

    @api.onchange('total_expense','line_ids')
    def _onchange_total_expense(self):
        self.update_expense_net()

    def action_start(self):
        for rec in self:
            rec.state = 'on_period'

    def action_close(self):
        for rec in self:
            curr_month = time.gmtime()[1]
            curr_year = time.gmtime()[0]

            if int(rec.month) >= curr_month and rec.year >= curr_year:
                raise ValidationError(_("Anda tidak bisa menutup report untuk bulan berjalan atau belum berjalan."))
            else:
                self.calculate_sale()
                rec.state = 'close'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def create(self, vals):
        res = super(SalesReport, self).create(vals)
        return res

    @api.constrains('month', 'year', 'marketplace_id')
    def check_name(self):
        for rec in self:
            value_check = self.env['sales.report'].search([('month', '=', rec.month), ('year', '=', rec.year), ('marketplace_id', '=', rec.marketplace_id.id), ('id', '!=', rec.id)])
            if value_check:
                raise ValidationError(_("Sudah ada report penjualan %s dengan Periode %s %s " % (rec.marketplace_id.name, self.month2name(int(rec.month)), rec.year)))

    def name_get(self):
        result = []
        for rec in self:
            name = self.month2name(int(rec.month)) + ' ' + str(rec.year)
            result.append((rec.id, name))
        return result

    def calculate_sale(self):
        for rec in self:
            jumlah_hari = lengthmonth(rec.year, int(rec.month))
            account = self.env['account.move']

            for ac in range(1, jumlah_hari + 1):
                ac_date = date(rec.year, int(rec.month), ac)
                filter_account = account.search([('invoice_date', '=', ac_date)])

                sum_amount_total = 0
                for fa in filter_account:
                    sum_amount_total += fa.amount_total

                disc = 0
                modal_jual = 0
                biaya_admin = 0
                net = sum_amount_total - modal_jual - disc - biaya_admin

                line_check = self.env['sales.report.line'].search([('date', '=', ac_date)])

                if line_check:
                    upd_vals = {'date': ac_date,
                                'jual': sum_amount_total,
                                'disc': disc,
                                'modals': modal_jual,
                                'biaya_admin': biaya_admin,
                                'net': net,
                                'sales_report_line_id': rec.id
                                }

                    line_check.write(upd_vals)
                else:
                    val = {'date': ac_date,
                           'jual': sum_amount_total,
                           'disc': disc,
                           'modals': modal_jual,
                           'biaya_admin': biaya_admin,
                           'net': net,
                           'sales_report_line_id': rec.id
                           }

                    self.env['sales.report.line'].create(val)

            self.update_expense_net()

    def update_expense_net(self):
        for rec in self:
            net_total = 0
            for line_id in rec.line_ids:
                net_total += line_id.net

            rec.total_net_sell = net_total - rec.total_expense

class SalesReportLine(models.Model):
    _description = 'Sales Report Line'
    _name = 'sales.report.line'

    sales_report_line_id = fields.Many2one(
        'sales.report', 'Sales Report', readonly=True,
    )

    date = fields.Date('Date', readonly=True, )
    jual = fields.Float('Jual', readonly=True, )
    disc = fields.Float('Disc', readonly=True, )
    modals = fields.Float('Modal', readonly=True, )
    net = fields.Float('Net', readonly=True, )
    biaya_admin = fields.Float('Biaya Admin', readonly=True, )
