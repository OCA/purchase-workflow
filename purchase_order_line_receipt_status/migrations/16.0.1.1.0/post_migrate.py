# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from openupgradelib import openupgrade


@openupgrade.logging()
def set_nothing_value(env):
    lines = env["purchase.order.line"].search([("receipt_status", "=", "")])
    lines._compute_receipt_status()


@openupgrade.migrate()
def migrate(env, version):
    set_nothing_value(env)
