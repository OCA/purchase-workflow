# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Field

get_depends_original = Field.get_depends


def get_depends(self, model):
    """Override of the Python method to remove the dependency of the unit fields.
    We also need to add product_id as depends, so that the initial computation is done.
    """
    depends, depends_context = get_depends_original(self, model)
    if model._name == "purchase.order.line" and self.name in {
        "name",
        "date_planned",
        "price_unit",
        "discount",
    }:
        if "product_qty" in depends:
            depends.remove("product_qty")
        if "product_uom" in depends:
            depends.remove("product_uom")
        # We need to add product_id to the depends to get the initial values
        if "product_id" not in depends:
            depends.append("product_id")
    return depends, depends_context


# Monkey-patching of the method
Field.get_depends = get_depends
