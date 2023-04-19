# Copyright (C) 2021-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, registry):
    with api.Environment.manage():
        # Unhide menu item for request for quotation and restore sequence
        env = api.Environment(cr, SUPERUSER_ID, {})
        env.ref("purchase.menu_purchase_rfq").write(
            {
                "groups_id": [(5,)],
                "sequence": 0,
            }
        )
        # ReCreate ir.actions.report
        env.ref("purchase.report_purchase_quotation").create_action()
