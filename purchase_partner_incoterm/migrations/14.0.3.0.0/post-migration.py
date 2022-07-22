# Copyright 2022 Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    children = env["res.partner"].search(
        [["commercial_partner_id", "!=", False], ["purchase_incoterm_id", "!=", False]]
    )

    seen = env["res.partner"].browse(False)

    for child in children:
        if child.parent_id.purchase_incoterm_id:
            continue
        if child.parent_id in seen:
            continue
        seen |= child.parent_id
        child.parent_id.purchase_incoterm_id = child.purchase_incoterm_id
        child.parent_id.purchase_incoterm_address_id = (
            child.purchase_incoterm_address_id
        )
