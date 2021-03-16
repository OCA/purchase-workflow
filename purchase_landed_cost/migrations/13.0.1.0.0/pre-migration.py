# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(
        env.cr,
        {
            "purchase_cost_distribution_expense": [
                ("invoice_line", None),
                ("invoice_id", None),
            ]
        },
    )
