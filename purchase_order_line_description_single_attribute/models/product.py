from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()
        product_lang = product_lang.with_context(include_single_value=True)
        res = super(PurchaseOrderLine, self)._get_product_purchase_description(
            product_lang
        )
        return res


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _get_combination_name(self):
        if self.env.context.get("include_single_value"):
            ptavs = self._without_no_variant_attributes().with_prefetch(
                self._prefetch_ids
            )
            return ", ".join([ptav.name for ptav in ptavs])
        else:
            return super(ProductTemplateAttributeValue, self)._get_combination_name()
