# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade, openupgrade_180


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.table_exists(env.cr, "ir_property"):
        openupgrade_180.convert_company_dependent(
            env, "product.template", "purchase_request"
        )
