
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource

class ShopeeAttributeVariant(models.Model):
    _name = "shopee.attribute.variant"
    _description = "Product Attribute"
    # if you change this _order, keep it in sync with the method
    # `_sort_key_attribute_value` in `product.template`
    _order = 'sequence, id'

    name = fields.Char('Attribute', required=True, translate=True)
    value_ids = fields.One2many('shopee.attribute.value.variant', 'shopee_attribute_id', 'Values', copy=True)
    sequence = fields.Integer('Sequence', help="Determine the display order", index=True)
    attribute_line_ids = fields.One2many('product.template.attribute.line', 'attribute_id', 'Lines')



class ShopeeAttributeValueVariant(models.Model):
    _name = "shopee.attribute.value.variant"
    _description = "Shopee Attribute value variant"
    # if you change this _order, keep it in sync with the method
    # `_sort_key_variant` in `product.template'
    _order = 'shopee_attribute_id, sequence, id'

    name = fields.Char(string='Value', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', help="Determine the display order", index=True)
    shopee_attribute_id = fields.Many2one('shopee.attribute.variant', string="Attribute", ondelete='cascade', required=True, index=True,
        help="The attribute cannot be changed once the value is used on at least one product.")



    def name_get(self):
        """Override because in general the name of the value is confusing if it
        is displayed without the name of the corresponding attribute.
        Eg. on product list & kanban views, on BOM form view

        However during variant set up (on the product template form) the name of
        the attribute is already on each line so there is no need to repeat it
        on every value.
        """
        if not self._context.get('show_attribute', True):
            return super(ShopeeAttributeValueVariant, self).name_get()
        return [(value.id, "%s: %s" % (value.shopee_attribute_id.name, value.name)) for value in self]






class ShopeeAttributeVariantProduct(models.Model):
    _name = "shopee.attribute.variant.product"
    _description = "Shopee variant in Product"

    product_tmpl_id = fields.Many2one('product.template', string="Product Template", ondelete='cascade', required=True,
                                      index=True)

    attribute_id2 = fields.Many2one('product.attribute', string="Attribute", ondelete='restrict', required=True,
                                   index=True)
    value_ids2 = fields.Many2many('product.attribute.value', string="Values",
                                 domain="[('attribute_id', '=', attribute_id2)]",
                                 relation='product_variant_attribute_line_rel', ondelete='cascade')

    shopee_variant_value_detail_ids2 = fields.One2many('shopee.value.variant.product', 'attribute_id', 'Variant Detail')
    # product_template_value_ids = fields.One2many('product.template.attribute.value', 'attribute_line_id',
    #                                              string="Product Attribute Values")


class ShopeeValueVariantProduct(models.Model):
    _name = "shopee.value.variant.product"
    _description = "Shopee Value in Product Detail"



    attribute_id = fields.Many2one('shopee.attribute.variant.product', string="Attribute", ondelete='cascade',
                                   index=True)
    value_id2 = fields.Many2one('product.attribute.value', string="Value", ondelete='restrict',
                               index=True)

    tier = fields.Char('Tier')
    tier_tobe = fields.Integer('Tier Tobe' )

    image_1920 = fields.Image('Image')
    # product_template_value_ids = fields.One2many('product.template.attribute.value', 'attribute_line_id',

    def write(self, vals):
        print(vals)
        if 'tier_tobe' in vals:
            tier_tobe = vals.get('tier_tobe')
            if self.attribute_id:
                if self.attribute_id.product_tmpl_id:
                    self.attribute_id.product_tmpl_id.changevariant_shopee=True
                    self.attribute_id.product_tmpl_id.variant_ok=True

        res = super(ShopeeValueVariantProduct, self).write(vals)
        return res


    @api.model
    def create(self, vals):
        print(vals)
        if vals.get('attribute_id'):
            prd_attribute = self.env['shopee.attribute.variant.product'].search([('id','=',vals.get('attribute_id'))])
            if prd_attribute:
                prd_attribute.product_tmpl_id.changevariant_shopee=True
                prd_attribute.product_tmpl_id.variant_ok=True
                arrayvariant=[]
                for variant in prd_attribute.value_ids2:
                    arrayvariant.append(variant.id)
                arrayvariant.append(vals.get('value_id2'))
                print(arrayvariant)
                prd_attribute.value_ids2=[(6,0,arrayvariant)]


        return super(ShopeeValueVariantProduct, self).create(vals)

    def unlink(self):
        for record in self:

            if record.attribute_id:
                if record.attribute_id.product_tmpl_id:
                    record.attribute_id.product_tmpl_id.changevariant_shopee = True
                    record.attribute_id.product_tmpl_id.variant_ok = True
                    record.attribute_id.value_ids2=[(3,record.value_id2.id)]
                seq = 0

                for value2 in record.attribute_id.shopee_variant_value_detail_ids2:
                    print(value2.tier)
                    print(value2.tier_tobe)
                for value2 in record.attribute_id.shopee_variant_value_detail_ids2:

                    value2.tier_tobe=seq
                    seq+=1
        super(ShopeeValueVariantProduct, self).unlink()

    def delete_variant_act(self):
        self.attribute_id.value_ids2=[(3,self.value_id2.id)]
        self.attribute_id.product_tmpl_id.changevariant_shopee=True
        self.attribute_id.product_tmpl_id.variant_ok=True
        self.unlink()

        return {'type': 'ir.actions.act_window_close'}

class ShopeeAttributeVariantDetail(models.Model):
    _name = "shopee.attribute.variant.detail"
    _description = "Shopee variant in Product Detail"


    product_tmpl_id = fields.Many2one('product.template', string="Product Template", ondelete='cascade', required=True,
                                      index=True)

    product_id = fields.Many2one('product.product', string="Product", )
    model_id = fields.Char(string="Model ID", )
    value_ids = fields.Many2many('product.attribute.value', string="Values",
                                 relation='shopee_attribute_value_detail_rel',
                                 ondelete='cascade')

    tier = fields.Char('Tier')
    tier_tobe = fields.Char('Tier tobe')
    shopee_price = fields.Float('Shopee Price', digits='Product Price')

    # image_1920 = fields.Image(default=_default_image)
    # product_template_value_ids = fields.One2many('product.template.attribute.value', 'attribute_line_id',
    #                                              string="Product Attribute Values")

 #                                              string="Product Attribute Values")