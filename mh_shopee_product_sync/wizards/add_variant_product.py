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
            attribute_variant_shopee = self.env['shopee.attribute.variant'].search(
                [('name', '=', lne.attribute_id.name)])

            values_shopee = []
            detail_variant = []
            if attribute_variant_shopee:
                attribute_id_shopee = attribute_variant_shopee[0]
                tier = 0
                for value in lne.value_ids:
                    attribute_variant_value_shopee = self.env['shopee.attribute.value.variant'].search(
                        [('name', '=', value.name), ('shopee_attribute_id', '=', attribute_id_shopee.id)])

                    if attribute_variant_value_shopee:

                        values_shopee.append(attribute_variant_value_shopee[0].id)
                        idvalues = attribute_variant_value_shopee[0].id
                    else:
                        id_value_shopee = self.env['shopee.attribute.value.variant'].create({'name': value.name,
                                                                                             'shopee_attribute_id': attribute_id_shopee.id})

                        values_shopee.append(id_value_shopee.id)
                        idvalues = id_value_shopee.id
                    detailvariant = (0, 0, {'value_id': idvalues, 'tier': tier})
                    detail_variant.append(detailvariant)
                    tier += 1


            else:
                attribute_id_shopee = self.env['shopee.attribute.variant'].create({'name': lne.attribute_id.name})
                tier = 0
                for value in lne.value_ids:
                    id_value_shopee = self.env['shopee.attribute.value.variant'].create(
                        {'name': value.name,
                         'shopee_attribute_id': attribute_id_shopee.id})

                    values_shopee.append(id_value_shopee.id)
                    detailvariant = (0, 0, {'value_id': id_value_shopee.id, 'tier': tier})
                    detail_variant.append(detailvariant)
                    tier += 1
            vals2.append((0, 0, {'attribute_id': attribute_id_shopee.id, 'value_ids': [(6, 0, values_shopee)],
                                 'shopee_variant_value_detail_ids': detail_variant}))

        product_obj.attribute_line_ids = vals
        product_obj.shopee_variant_product_ids = vals2
        values_shop_all = []
        for variant_shop in product_obj.shopee_variant_product_ids:

            values_shop = []
            for value_shop in variant_shop.value_ids:
                values_shop.append(value_shop.id)
            values_shop_all.append(values_shop)
        tier1 = 0
        tierstr = []
        print((values_shop_all))
        print(len(values_shop_all))
        if len(values_shop_all) > 1:
            for v0 in values_shop_all[0]:

                tier2 = 0
                for v1 in values_shop_all[1]:
                    vals_shop = [v0] + [v1]
                    tierstr = str(tier1) + "," + str(tier2)
                    tier2 += 1
                    vals3.append((0, 0, {'shopee_price': product_obj.shopee_price, 'tier': tierstr,
                                         'value_ids': [(6, 0, vals_shop)]}))

                tier1 += 1
        else:

            for v0 in values_shop_all[0]:
                vals_shop = [v0]
                tierstr = str(tier1)
                vals3.append((0, 0, {'shopee_price': product_obj.shopee_price, 'tier': tierstr,
                                     'value_ids': [(6, 0, vals_shop)]}))

                tier1 += 1
            print(vals3)
        print("==================")
        product_obj.shopee_variant_product_detail_ids = vals3
        for p in product_obj.shopee_variant_product_detail_ids:
            valuear=[]
            for at in p.value_ids:
                valuear.append(at.name)

            print(valuear)
            print("=============+++++++")
            product_ids=self.env['product.product'].search([('product_tmpl_id','=',self.env.context['active_ids'])])
            for prd in product_ids:
                valueprd=[]
                for atprd in prd.product_template_attribute_value_ids:
                    valueprd.append(atprd.name)
                sama=True
                for x in valueprd:
                    if x not in valuear:
                        sama = False
                if sama:
                    p.product_id=prd.id

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
