import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    # Remove the old stored field if it exists
    if sql.column_exists(cr, "purchase_order_line", "line_receipt_status"):
        return

    _logger.info("Add line_receipt_status column on purchase_order_line table")

    cr.execute(
        """
        ALTER TABLE purchase_order_line
        ADD COLUMN line_receipt_status VARCHAR;
        """
    )

    _logger.info("line_receipt_status column added successfully")
    _logger.info("initializing line_receipt_status values...")
    query = """
        UPDATE purchase_order_line pol
        SET line_receipt_status = sub.status
        FROM (
            SELECT
                pol.id as line_id,
                CASE
                    WHEN COUNT(im.id) = 0 OR BOOL_AND(im.state = 'cancel')
                        THEN NULL
                    WHEN pol.qty_received = 0 AND BOOL_OR(im.state NOT IN ('cancel','done'))
                        THEN 'pending'
                    WHEN BOOL_OR(im.state NOT IN ('cancel','done'))
                        THEN 'partial'
                    ELSE 'full'
                END AS status
            FROM purchase_order_line pol
                LEFT JOIN stock_move im ON im.purchase_line_id = pol.id
                LEFT JOIN stock_picking sp ON sp.id = im.picking_id
                LEFT JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
            WHERE spt.code = 'incoming'
            GROUP BY pol.id, pol.qty_received
        ) sub
        WHERE pol.id = sub.line_id;
    """
    cr.execute(query)
    _logger.info(
        "line_receipt_status values initialized successfully (%d rows updated)",
        cr.rowcount,
    )
