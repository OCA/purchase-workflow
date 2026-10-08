# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)

try:
    from odoo.upgrade.util.pg import explode_execute

    def _execute(cr, query):
        return explode_execute(
            cr,
            query,
            table="product_supplierinfo",
            alias="ps",
            logger=_logger,
        )
except ImportError:

    def _execute(cr, query):
        cr.execute(query)
        return cr.rowcount


def post_init_hook(env):
    """Backfill is_product_active for all existing supplierinfo rows.

    Two passes — see module README for the rationale.
    Uses explode_execute when available to process millions of rows in
    parallel buckets without locking the whole table at once.
    """
    count = _execute(
        env.cr,
        """
        UPDATE product_supplierinfo ps
        SET    is_product_active = false
        FROM   product_template pt
        WHERE  ps.product_tmpl_id = pt.id
          AND  pt.active = false
        """,
    )
    _logger.info(
        "product_supplierinfo_active_index: %s inactive-template rows updated",
        count,
    )

    count = _execute(
        env.cr,
        """
        UPDATE product_supplierinfo ps
        SET    is_product_active = false
        FROM   product_product pp
        WHERE  ps.product_id = pp.id
          AND  pp.active = false
        """,
    )
    _logger.info(
        "product_supplierinfo_active_index: %s inactive-variant rows updated",
        count,
    )
