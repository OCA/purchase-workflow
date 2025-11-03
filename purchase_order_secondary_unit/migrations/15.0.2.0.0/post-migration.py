# Copyright 2025 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Set default purchase secondary uom from template to variants.
    # purchase_secondary_uom_id is no longer stored on product.template, so
    # the legacy values must be read straight from the column, which is
    # still physically present at this point (Odoo never drops it).
    env.cr.execute(
        "SELECT id, purchase_secondary_uom_id FROM product_template"
        " WHERE purchase_secondary_uom_id IS NOT NULL"
    )
    legacy_values = dict(env.cr.fetchall())
    templates = (
        env["product.template"].with_context(acive_test=False).browse(legacy_values)
    )
    unique_variants = templates.filtered(lambda tmpl: tmpl.product_variant_count == 1)
    for template in unique_variants:
        legacy_secondary_uom_id = legacy_values[template.id]
        if template.product_variant_ids.purchase_secondary_uom_id.id != (
            legacy_secondary_uom_id
        ):
            # Force store purchase_secondary_uom_id for unique variants
            template.product_variant_ids.purchase_secondary_uom_id = (
                legacy_secondary_uom_id
            )
    # purchase secondary uom computattion in product template for products
    # with more than one variant
    (templates - unique_variants)._compute_purchase_secondary_uom_id()
