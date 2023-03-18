# -*- coding: utf-8 -*-

from odoo import models
class SalesReportXlsx(models.AbstractModel):
    _name = 'report.shopee_report.report_sales_order_xls'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, sales):
        bold = workbook.add_format({'bold': True})
        date_style = workbook.add_format({'text_wrap': True, 'num_format': 'dd-mm-yyyy'})
        money_format = workbook.add_format({'text_wrap': True, 'num_format': '#,##0.00'})
        money_format_bold = workbook.add_format({'text_wrap': True, 'num_format': '#,##0.00', 'bold': True})

        for obj in sales:
            month_name = obj.month2name(int(obj.month))
            report_name = month_name + ' ' + str(obj.year)
            sheet = workbook.add_worksheet(report_name)

            row = 1
            col = 1
            sheet.set_column('B:B', 25)
            sheet.set_column('C:C', 15)
            sheet.set_column('D:D', 15)
            sheet.set_column('E:E', 15)
            sheet.set_column('F:F', 15)
            sheet.set_column('G:G', 15)

            row += 1
            sheet.merge_range(row, col, row, col + 1, 'Sales Report', bold)

            row += 2
            sheet.write(row, col, 'Marketplace Account', bold)
            sheet.write(row, col + 1, obj.marketplace_id.name)

            row += 1
            sheet.write(row, col, 'Period', bold)
            sheet.write(row, col + 1, month_name + ' ' + str(obj.year))

            row += 2
            sheet.write(row, col, 'Date', bold)
            col += 1
            sheet.write(row, col, 'Jual', bold)
            col += 1
            sheet.write(row, col, 'Disc', bold)
            col += 1
            sheet.write(row, col, 'Modal', bold)
            col += 1
            sheet.write(row, col, 'Biaya Admin', bold)
            col += 1
            sheet.write(row, col, 'Net', bold)

            jual_total = 0
            disc_total = 0
            modal_total = 0
            admin_total = 0
            net_total = 0

            for line in obj.line_ids:
                jual_total += line.jual
                disc_total += line.disc
                modal_total += line.modals
                admin_total += line.biaya_admin
                net_total += line.net

                row += 1
                sheet.write(row, col - 5, line.date, date_style)
                sheet.write(row, col - 4, line.jual, money_format)
                sheet.write(row, col - 3, line.disc, money_format)
                sheet.write(row, col - 2, line.modals, money_format)
                sheet.write(row, col - 1, line.biaya_admin, money_format)
                sheet.write(row, col, line.net, money_format)

            row += 1
            sheet.write(row, col - 4, jual_total, money_format_bold)
            sheet.write(row, col - 3, disc_total, money_format_bold)
            sheet.write(row, col - 2, modal_total, money_format_bold)
            sheet.write(row, col - 1, admin_total, money_format_bold)
            sheet.write(row, col, net_total, money_format_bold)

            row += 2
            sheet.write(row, col - 5, 'Total Expense', bold)
            sheet.write(row, col - 4, obj.total_expense, money_format_bold)
            row += 1
            sheet.write(row, col - 5, 'Total Net Sell', bold)
            sheet.write(row, col - 4, obj.total_net_sell, money_format_bold)
