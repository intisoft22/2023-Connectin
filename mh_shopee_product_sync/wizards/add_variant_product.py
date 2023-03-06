from odoo import fields, models, api


class AddVariantProduct(models.TransientModel):
    _name = 'add.variant.product'
    _description = 'Add Variant in Product'

    attribute_line_ids = fields.One2many('add.variant.product.line', 'product_tmpl_id', 'Product Attributes', copy=True)



    def add_variant(self):
        product_obj = self.env['product.template'].search([('id', '=', self.env.context['active_ids'])])
        print(product_obj)
        product_obj.attribute_line_ids = False
        product_obj.shopee_variant_product_ids = False
        product_obj.shopee_variant_product_detail_ids = False
        vals = []
        vals2 = []
        vals3 = []
        for lne in self.attribute_line_ids:
            values = []
            for value in lne.value_ids:
                values.append(value.id)
            vals.append((0, 0, {'attribute_id': lne.attribute_id.id, 'value_ids': [(6, 0, values)]}))
            attribute_variant_shopee = self.env['shopee.attribute.variant'].search([('name', '=', lne.attribute_id.name)])

            values_shopee = []
            if attribute_variant_shopee:
                attribute_id_shopee = attribute_variant_shopee[0]

                for value in lne.value_ids:
                    attribute_variant_value_shopee = self.env['shopee.attribute.value.variant'].search(
                        [('name', '=', value.name), ('shopee_attribute_id', '=', attribute_id_shopee.id)])
                    if attribute_variant_value_shopee:

                        values_shopee.append(attribute_variant_value_shopee[0].id)
                    else:
                        id_value_shopee = self.env['shopee.attribute.value.variant'].create({'name': value.name,
                                                                                                 'shopee_attribute_id': attribute_id_shopee.id})

                        values_shopee.append(id_value_shopee.id)


            else:
                attribute_id_shopee = self.env['shopee.attribute.variant'].create({'name': lne.attribute_id.name})

                for value in lne.value_ids:
                    id_value_shopee  = self.env['shopee.attribute.value.variant'].create(
                        {'name': value.name,
                         'shopee_attribute_id': attribute_id_shopee.id})

                    values_shopee.append(id_value_shopee.id)
            vals2.append((0, 0, {'attribute_id': attribute_id_shopee.id, 'value_ids': [(6, 0, values_shopee)]}))

        product_obj.attribute_line_ids = vals
        product_obj.shopee_variant_product_ids = vals2
        values_shop_all = []
        for variant_shop in product_obj.shopee_variant_product_ids :

            values_shop=[]
            for value_shop  in variant_shop.value_ids:
                values_shop.append(value_shop.id)
            values_shop_all.append(values_shop)
        for v0 in values_shop_all[0]:
            for v1 in values_shop_all[1]:
                vals_shop = [v0]+[ v1]
                vals3.append((0, 0, {'shopee_price': product_obj.shopee_price, 'value_ids': [(6, 0, vals_shop)]}))
        product_obj.shopee_variant_product_detail_ids = vals3

        return {'type': 'ir.actions.act_window_close'}


class AddVariantProductLine(models.TransientModel):
    _name = 'add.variant.product.line'
    _description = 'Add Variant in Product'

    product_tmpl_id = fields.Many2one('add.variant.product', string="Product Template", ondelete='cascade',
                                      required=True, index=True)
    attribute_id = fields.Many2one('product.attribute', string="Attribute", ondelete='restrict', required=True,
                                   index=True)
    value_ids = fields.Many2many('product.attribute.value', string="Values",
                                 domain="[('attribute_id', '=', attribute_id)]",
                                 relation='add_variant_attribute_line_rel', ondelete='restrict')
