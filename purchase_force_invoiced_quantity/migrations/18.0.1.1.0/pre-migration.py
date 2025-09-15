# Copyright 2025 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def migrate_force_invoiced_to_force_invoiced_qty(cr):
    old_field_exists = column_exists(cr, "purchase_order_line", "force_invoiced")
    new_field_exists = column_exists(cr, "purchase_order_line", "force_invoiced_qty")
    if old_field_exists and not new_field_exists:
        _logger.info(
            "Renaming force_invoiced field to force_invoiced_qty in purchase_order_line"
        )
        cr.execute(
            "ALTER TABLE purchase_order_line "
            "RENAME COLUMN force_invoiced TO force_invoiced_qty"
        )
        _logger.info("Successfully renamed force_invoiced to force_invoiced_qty")
    if new_field_exists:
        _logger.info("Field force_invoiced_qty already exists, skipping migration")
    if not old_field_exists:
        _logger.info("Field force_invoiced does not exist, skipping migration")


def migrate(cr, version):
    migrate_force_invoiced_to_force_invoiced_qty(cr)
