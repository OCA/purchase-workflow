# Copyright 2024-Today - Sylvain Le GAL (GRAP)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("Initializing column main_seller_id on table product_template")
    cr.execute(
        """
        ALTER TABLE product_template
        ADD COLUMN IF NOT EXISTS main_seller_id integer;
        """
    )
    cr.execute(
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

        UPDATE product_template pt
        SET main_seller_id = first_supplierinfos.partner_id
        FROM first_supplierinfos
        WHERE pt.id = first_supplierinfos.product_tmpl_id;
        """
    )
