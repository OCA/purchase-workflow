# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from openupgradelib import openupgrade

_field_renames = [
    ("purchase.order", "purchase_order", "reception_status", "receipt_status"),
]


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(env.cr, "purchase_order", "receipt_status"):
        openupgrade.rename_fields(env, _field_renames)
