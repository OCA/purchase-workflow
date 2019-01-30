# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from psycopg2.extensions import AsIs
import logging
logger = logging.getLogger(__name__)


def rename_column_request_line_procurement(cr):
    rename = "openupgrade_legacy_11_0_procurement_id"
    logger.info(
        "table purchase_request_line, column procurement_id: renaming to %s",
        rename)

    cr.execute(
        'ALTER TABLE purchase_request_line RENAME procurement_id TO %s',
        (AsIs(rename), ),
    )
    cr.execute(
        'DROP INDEX IF EXISTS purchase_request_line_procurement_id_index')


def migrate(cr, version):
    if not version:
        return
    rename_column_request_line_procurement(cr)
