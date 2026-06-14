# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_noupdate_xmlids = [
    "mt_request_to_approve",
    "mt_request_approved",
    "mt_request_rejected",
    "mt_request_done",
]


@openupgrade.migrate()
def migrate(cr, version):
    # Workaround to execute the migration script without errors
    # see https://github.com/odoo/odoo/blob/2a839ef1ed09c36f27ce7536ca3052d9f65ceed9/odoo/modules/migration.py#L252-L256
    env = cr
    openupgrade.set_xml_ids_noupdate_value(
        env, "purchase_request", _noupdate_xmlids, True
    )
