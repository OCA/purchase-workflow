# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools.sql import column_exists


def migrate(cr, version):
    if not column_exists(cr, "purchase_order_line", "secondary_uom_price"):
        cr.execute("""
            ALTER TABLE purchase_order_line
            ADD COLUMN secondary_uom_price double precision;

            UPDATE purchase_order_line pol
            SET secondary_uom_price = pol.price_unit * su.factor
            FROM product_secondary_unit su
            WHERE su.id = pol.secondary_uom_id;
        """)
