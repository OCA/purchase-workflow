# Copyright 2025 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Set default purchase secondary uom from template to variants
    templates = (
        env["product.template"]
        .with_context(active_test=False)
        .search([("purchase_secondary_uom_id", "!=", False)])
    )
    unique_variants = templates.filtered(lambda tmpl: tmpl.product_variant_count == 1)
    for template in unique_variants:
        if (
            template.product_variant_ids.purchase_secondary_uom_id
            != template.purchase_secondary_uom_id
        ):
            # Force store purchase_secondary_uom_id for unique variants
            template.product_variant_ids.purchase_secondary_uom_id = (
                template.purchase_secondary_uom_id
            )
    # purchase secondary uom computation in product template for products
    # with more than one variant
    (templates - unique_variants)._compute_purchase_secondary_uom_id()
