# Copyright 2025 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Purchase lines used the variant value and fell back to the template one,
    # so only variants without their own value inherit it from the template.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_product pp
        SET purchase_secondary_uom_id = pt.purchase_secondary_uom_id
        FROM product_template pt
        WHERE pt.id = pp.product_tmpl_id
            AND pp.purchase_secondary_uom_id IS NULL
            AND pt.purchase_secondary_uom_id IS NOT NULL
        """,
    )
    env.cr.execute(
        """
        SELECT DISTINCT product_tmpl_id
        FROM product_product
        WHERE purchase_secondary_uom_id IS NOT NULL
        """
    )
    templates = env["product.template"].browse([row[0] for row in env.cr.fetchall()])
    # Queue the recomputation instead of calling the compute method: assigning
    # outside the recomputation runs the inverse and overwrites the variants.
    env.add_to_compute(templates._fields["purchase_secondary_uom_id"], templates)
    templates.flush_recordset(["purchase_secondary_uom_id"])
