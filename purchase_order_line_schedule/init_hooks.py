# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
import logging

_logger = logging.getLogger(__name__)


def pre_create_schedule_lines(cr):
    _logger.info(
        "Pre-creating purchase.order.line.schedule records for "
        "existing purchase orders"
    )
    cr.execute(
        """
        INSERT INTO purchase_order_line_schedule
            (create_uid, create_date, write_uid, write_date,
             order_id, order_line_id, date_planned, product_qty,
             qty_received_manual, product_id, company_id)
        SELECT create_uid, create_date, write_uid, write_date,
               order_id, id, date_planned, product_qty,
               qty_received_manual, product_id, company_id
        FROM purchase_order_line
    """
    )


def post_init_hook(cr, registry):
    """ Set value for order_sequence on old records """
    pre_create_schedule_lines(cr)
