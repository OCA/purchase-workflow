# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from openupgradelib import openupgrade

_field_renames = [
    (
        "purchase.order.line",
        "purchase_order_line",
        "reception_status",
        "receipt_status",
    ),
]

_value_mapping = {
    "no": "pending",
    "partial": "partial",
    "received": "full",
    "over": "over",
}


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "purchase_order_line", "reception_status"):
        openupgrade.rename_fields(env, _field_renames)
        for old_value, new_value in _value_mapping.items():
            if old_value != new_value:
                openupgrade.logged_query(
                    env.cr,
                    """
                    UPDATE purchase_order_line
                    SET receipt_status = %s
                    WHERE receipt_status = %s
                    """,
                    (new_value, old_value),
                )
