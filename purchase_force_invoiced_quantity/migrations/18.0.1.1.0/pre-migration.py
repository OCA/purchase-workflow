# Copyright 2025 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate_force_invoiced_to_force_invoiced_qty(cr):
    cr.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'purchase_order_line'
        AND column_name = 'force_invoiced'
        """
    )
    old_field_exists = cr.fetchone()
    cr.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'purchase_order_line'
        AND column_name = 'force_invoiced_qty'
        """
    )
    new_field_exists = cr.fetchone() is not None
    if old_field_exists and not new_field_exists:
        _logger.info(
            "Migrating force_invoiced field to force_invoiced_qty "
            "in purchase_order_line"
        )
        cr.execute(
            """
            ALTER TABLE purchase_order_line
            ADD COLUMN IF NOT EXISTS force_invoiced_qty numeric DEFAULT 0.0
            """
        )
        cr.execute(
            """
            UPDATE purchase_order_line
            SET force_invoiced_qty = COALESCE(force_invoiced, 0.0)
            WHERE force_invoiced IS NOT NULL
            """
        )
        cr.execute(
            "ALTER TABLE purchase_order_line DROP COLUMN IF EXISTS force_invoiced"
        )
        _logger.info("Successfully migrated force_invoiced to force_invoiced_qty")
    elif new_field_exists:
        _logger.info("Field force_invoiced_qty already exists, skipping migration")
    else:
        _logger.info(
            "No force_invoiced field found in purchase_order_line, skipping migration"
        )


def migrate(cr, version):
    migrate_force_invoiced_to_force_invoiced_qty(cr)
