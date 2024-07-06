# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        WITH numbered_supplierinfos as (
            SELECT *, ROW_number() over (
                partition BY product_tmpl_id
                ORDER BY sequence, min_qty desc, price
            ) as row_number
            FROM product_supplierinfo
        ),

        first_supplierinfos as (
            SELECT * from numbered_supplierinfos
            WHERE row_number = 1
        )

        UPDATE product_product pp
        SET product_main_seller_partner_id = first_supplierinfos.name
        FROM first_supplierinfos
        WHERE pp.product_tmpl_id = first_supplierinfos.product_tmpl_id
        AND pp.product_main_seller_partner_id != first_supplierinfos.name;
        """,
    )
