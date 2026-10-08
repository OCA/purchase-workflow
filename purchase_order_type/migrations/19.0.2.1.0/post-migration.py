# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """The purchase order form always required an order type, so every
    existing company keeps requiring it. A fresh install does not.
    """
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.company"].with_context(active_test=False).search([]).write(
        {"purchase_order_type_required": True}
    )
