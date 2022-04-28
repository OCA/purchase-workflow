from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        for index, domain_triplet in enumerate(args):
            if domain_triplet[0] == "variant_seller_ids.name" and domain_triplet[2]:
                product_ids = []
                sup_infos = self.env["product.supplierinfo"].search(
                    [
                        ("name", "=", domain_triplet[2]),
                    ]
                )
                for sup_info in sup_infos:
                    if sup_info.product_id:
                        product_ids.append(sup_info.product_id.id)
                    else:
                        product_ids.extend(
                            sup_info.product_tmpl_id.product_variant_ids.ids
                        )
                args[index] = ["id", "in", product_ids]
        return super(ProductProduct, self)._name_search(
            name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )
