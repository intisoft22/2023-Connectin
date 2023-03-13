from odoo import fields, models, api,_

from odoo.exceptions import UserError

class AddVariantProduct(models.TransientModel):
    _name = 'add.variant.product'
    _description = 'Add Variant in Product'

    @api.model
    def default_get(self, fields):
        res = super(AddVariantProduct, self).default_get(fields)
        product_obj = self.env['product.template']
        product_ids = product_obj.search([('id', '=', self.env.context['active_ids'])])
        wizard = []
        for attr in product_ids.attribute_line_ids:
            value = []
            for x in attr.value_ids:
                value.append(x.id)
            wizard.append([0, 0, {'attribute_id': attr.attribute_id.id, 'value_ids': [(6, 0, value)]}])
        res['attribute_line_ids'] = wizard
        return res

    attribute_line_ids = fields.One2many('add.variant.product.line', 'add_attr_id', 'Product Attributes', copy=True)

    def add_variant(self):
        product_obj = self.env['product.template'].search([('id', '=', self.env.context['active_ids'])])
        print(product_obj)
        vals = []
        vals2 = []
        vals3 = []
        variantbeda=False
        for lne in self.attribute_line_ids:

            attrproduct_obj = self.env['product.template.attribute.line'].search(
                [('product_tmpl_id', '=', self.env.context['active_ids'][0]), ('attribute_id', '=', lne.attribute_id.id)])
            print((attrproduct_obj))
            valueattproduct=[]
            for ap in attrproduct_obj.value_ids:
                valueattproduct.append(ap.id)
            print(valueattproduct)
            for value in lne.value_ids:
                print(value.id)
                if value.id not in valueattproduct:
                    variantbeda=True
        if variantbeda:
            raise UserError(_('Variations Invalid'))
        for lne in self.attribute_line_ids:
            values = []
            detail_variant = []
            tier = 0
            for value in lne.value_ids:
                values.append(value.id)
                detailvariant = (0, 0, {'value_id2': value.id, 'tier': tier, 'tier_tobe': tier})
                detail_variant.append(detailvariant)
                tier += 1

            vals2.append((0, 0, {'attribute_id2': lne.attribute_id.id, 'value_ids2': [(6, 0, values)],
                                 'shopee_variant_value_detail_ids2': detail_variant}))

        product_obj.shopee_variant_product_ids = False
        product_obj.shopee_variant_product_detail_ids = False
        # product_obj.attribute_line_ids = vals
        product_obj.shopee_variant_product_ids = vals2
        values_shop_all = []
        for variant_shop in product_obj.shopee_variant_product_ids:

            values_shop = []
            for value_shop in variant_shop.value_ids2:
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
                    vals3.append((0, 0, {'shopee_price': product_obj.shopee_price, 'tier': tierstr, 'tier_tobe': tierstr,
                                         'value_ids': [(6, 0, vals_shop)]}))

                tier1 += 1
        else:

            for v0 in values_shop_all[0]:
                vals_shop = [v0]
                tierstr = str(tier1)
                vals3.append((0, 0, {'shopee_price': product_obj.shopee_price, 'tier': tierstr, 'tier_tobe': tierstr,
                                     'value_ids': [(6, 0, vals_shop)]}))

                tier1 += 1
            print(vals3)
        print("==================")
        product_obj.shopee_variant_product_detail_ids = vals3
        for p in product_obj.shopee_variant_product_detail_ids:
            valuear = []
            for at in p.value_ids:
                valuear.append(at.name)

            product_ids = self.env['product.product'].search([('product_tmpl_id', '=', self.env.context['active_ids'])])
            for prd in product_ids:
                valueprd = []
                if prd.product_template_attribute_value_ids:
                    for atprd in prd.product_template_attribute_value_ids:
                        valueprd.append(atprd.name)
                    sama = True
                    for x in valueprd:
                        if x not in valuear:
                            sama = False
                    if sama:
                        p.product_id = prd.id

        product_obj.needgenerate_shopee = False
        product_obj.needupdate_shopee = True
        product_obj.changevariant_shopee = False
        product_obj.variant_ok = False
        return {'type': 'ir.actions.act_window_close'}


class AddVariantProductLine(models.TransientModel):
    _name = 'add.variant.product.line'
    _description = 'Add Variant in Product'

    add_attr_id = fields.Many2one('add.variant.product', string="Product Template", ondelete='cascade',
                                  required=True, index=True)
    attribute_id = fields.Many2one('product.attribute', string="Attribute", ondelete='restrict', required=True,
                                   index=True)
    value_ids = fields.Many2many('product.attribute.value', string="Values",
                                 domain="[('attribute_id', '=', attribute_id)]",
                                 relation='add_variant_attribute_line_rel', ondelete='restrict')
