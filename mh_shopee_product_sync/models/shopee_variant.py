
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
    attribute_id = fields.Many2one('shopee.attribute.variant', string="Attribute", ondelete='cascade', required=True,
                                   index=True)
    value_ids = fields.Many2many('shopee.attribute.value.variant', string="Values",
                                 domain="[('shopee_attribute_id', '=', attribute_id)]",
                                 relation='shopee_attribute_value_product_template_attribute_line_rel',
                                 ondelete='restrict')

    shopee_variant_value_detail_ids = fields.One2many('shopee.value.variant.detail', 'attribute_id', 'Variant Detail')
    # product_template_value_ids = fields.One2many('product.template.attribute.value', 'attribute_line_id',
    #                                              string="Product Attribute Values")


class ShopeeAttributeVariantValueDetail(models.Model):
    _name = "shopee.value.variant.detail"
    _description = "Shopee Value in Product Detail"

    @api.model
    def _default_image(self):
        image_path = get_module_resource('lunch', 'static/img', 'lunch.png')
        return base64.b64encode(open(image_path, 'rb').read())

    attribute_id = fields.Many2one('shopee.attribute.variant.product', string="Attribute", ondelete='cascade',
                                   index=True)
    value_id = fields.Many2one('shopee.attribute.value.variant', string="Value", ondelete='restrict',
                               index=True)

    tier = fields.Integer('Tier')

    image_1920 = fields.Image(default=_default_image)
    # product_template_value_ids = fields.One2many('product.template.attribute.value', 'attribute_line_id',


class ShopeeAttributeVariantDetail(models.Model):
    _name = "shopee.attribute.variant.detail"
    _description = "Shopee variant in Product Detail"


    product_tmpl_id = fields.Many2one('product.template', string="Product Template", ondelete='cascade', required=True,
                                      index=True)
    attribute_id = fields.Many2one('shopee.attribute.variant', string="Attribute", ondelete='restrict',
                                   index=True)
    product_id = fields.Many2one('product.product', string="Product", )
    model_id = fields.Char(string="Model ID", )
    value_ids = fields.Many2many('shopee.attribute.value.variant', string="Values",
                                 relation='shopee_attribute_value_attribute_line_detail_rel',
                                 ondelete='restrict')

    tier = fields.Char('Tier')
    shopee_price = fields.Float('Shopee Price', digits='Product Price')

    # image_1920 = fields.Image(default=_default_image)
    # product_template_value_ids = fields.One2many('product.template.attribute.value', 'attribute_line_id',
    #                                              string="Product Attribute Values")

 #                                              string="Product Attribute Values")