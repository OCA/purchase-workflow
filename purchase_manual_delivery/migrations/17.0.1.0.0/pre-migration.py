from odoo.tools.sql import column_exists


def migrate(cr, version):
    """Initialize qty_in_receipt as existing_qty - qty_received"""
    if not column_exists(cr, "purchase_order_line", "qty_in_receipt") and column_exists(
        cr, "purchase_order_line", "existing_qty"
    ):
        cr.execute(
            """
            alter table purchase_order_line
            add column qty_in_receipt numeric;
            update purchase_order_line
            set qty_in_receipt = coalesce(existing_qty, 0) - coalesce(qty_received, 0);
            """
        )
