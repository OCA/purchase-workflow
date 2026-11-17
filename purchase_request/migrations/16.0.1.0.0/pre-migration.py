# Copyright 2026 Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_160


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(
        env.cr, "purchase_request_line", "analytic_account_id"
    ):
        openupgrade_160.fill_analytic_distribution(env, "purchase_request_line")
