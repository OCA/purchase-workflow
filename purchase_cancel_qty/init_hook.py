# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging


logger = logging.getLogger(__name__)


def init_ordered_qty(cr, pool):
    logger.info(
        "[INIT HOOK] purchase_cancel_qty: Update ordered_qty")
    cr.execute("""
        UPDATE purchase_order_line
        SET ordered_qty = product_qty
        WHERE state = 'purchase'
    """)


def post_init_hook(cr, pool):
    init_ordered_qty(cr, pool)
