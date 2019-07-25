# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openupgradelib import openupgrade


def store_field_qty_in_progress(cr):
    if not openupgrade.column_exists(
        cr, 'purchase_request_line', 'qty_in_progress'
    ):
        cr.execute(
            """
            ALTER TABLE purchase_request_line ADD COLUMN qty_in_progress float
            DEFAULT 0.0;
            """)

        cr.execute(
            """
            ALTER TABLE purchase_request_line ALTER COLUMN qty_in_progress
             DROP DEFAULT
            """)


def store_field_qty_done(cr):
    if not openupgrade.column_exists(
        cr, 'purchase_request_line', 'qty_done'
    ):
        cr.execute(
            """
            ALTER TABLE purchase_request_line ADD COLUMN qty_done float
            DEFAULT 0.0;
            """)

        cr.execute(
            """
            ALTER TABLE purchase_request_line ALTER COLUMN qty_done
             DROP DEFAULT
            """)


def store_field_qty_cancelled(cr):
    if not openupgrade.column_exists(
        cr, 'purchase_request_line', 'qty_cancelled'
    ):
        cr.execute(
            """
            ALTER TABLE purchase_request_line ADD COLUMN qty_cancelled float
            DEFAULT 0.0;
            """)

        cr.execute(
            """
            ALTER TABLE purchase_request_line ALTER COLUMN qty_cancelled
             DROP DEFAULT
            """)


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    store_field_qty_cancelled(cr)
    store_field_qty_done(cr)
    store_field_qty_in_progress(cr)
