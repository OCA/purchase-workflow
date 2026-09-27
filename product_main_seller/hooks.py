# Copyright 2024-Today - Sylvain Le GAL (GRAP)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    _logger.info("Initializing column main_seller_id on table product_template")
    cr = env.cr
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
    cr.execute(
        """
        ALTER TABLE product_product
        ADD COLUMN IF NOT EXISTS main_seller_id integer;
        """
    )
    cr.execute(
        """
        WITH ranked_supplierinfos AS (
        SELECT
            p.id AS product_id,
            psi.partner_id,
            ROW_NUMBER() OVER (
                PARTITION BY p.id
                ORDER BY
                    CASE
                        WHEN psi.product_id = p.id THEN 0
                        ELSE 1
                    END,
                    psi.sequence,
                    psi.min_qty DESC,
                    psi.price,
                    psi.id
            ) AS row_number
        FROM product_product p
        JOIN product_supplierinfo psi
            ON psi.product_tmpl_id = p.product_tmpl_id
            AND (
                psi.product_id = p.id
                OR psi.product_id IS NULL
            )
        JOIN res_partner rp
            ON rp.id = psi.partner_id
            AND rp.active
        WHERE
            (psi.date_start IS NULL OR psi.date_start <= CURRENT_DATE)
            AND (psi.date_end IS NULL OR psi.date_end >= CURRENT_DATE)
        )
        UPDATE product_product p
        SET main_seller_id = ranked_supplierinfos.partner_id
        FROM ranked_supplierinfos
        WHERE ranked_supplierinfos.product_id = p.id
        AND ranked_supplierinfos.row_number = 1;
        """
    )
