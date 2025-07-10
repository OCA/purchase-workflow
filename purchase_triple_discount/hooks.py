# Copyright 2024-Today - Sylvain Le GAL (GRAP)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Initializing column discount1 on table purchase_order_line")
    cr.execute(
        """
            UPDATE purchase_order_line
            SET discount1 = discount
            WHERE discount != 0
        """
    )
    _logger.info("Initializing column discount1 on table product_supplierinfo")
    cr.execute(
        """
            UPDATE product_supplierinfo
            SET discount1 = discount
            WHERE discount != 0
        """
    )
