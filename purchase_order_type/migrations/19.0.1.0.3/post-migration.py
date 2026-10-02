# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Keep the behavior existing installations had before this version.

    The purchase order form always required an order type, so every
    existing company keeps requiring it. Per company, the order type
    _default_order_type() used to return before is_default existed (the
    lowest-sequence type in that company's scope) is flagged as default, so
    it stays the type a new purchase order gets, now as an explicit,
    reconfigurable choice. A fresh install requires no order type and has no
    default until one is configured.
    """
    if not version:
        return
    cr.execute("UPDATE res_company SET purchase_order_type_required = TRUE")
    env = api.Environment(cr, SUPERUSER_ID, {})
    order_type = env["purchase.order.type"]
    # A database migrated from an earlier version that already had is_default
    # keeps its configured defaults; flagging the legacy picks on top of them
    # would break the one-default-per-company constraint.
    if order_type.search_count([("is_default", "=", True)]):
        return

    # Resolve every company first, flag afterwards. A company whose legacy
    # pick is the global type would otherwise mask the next company's own,
    # lower-sequence pick and silently change what that company resolves to.
    picks = {}
    for company in env["res.company"].search([]):
        legacy_default = order_type.search(
            [("company_id", "in", [False, company.id])], limit=1
        )
        if legacy_default:
            picks.setdefault(legacy_default.company_id.id, legacy_default)

    to_flag = order_type.browse()
    for legacy_default in picks.values():
        to_flag |= legacy_default
    to_flag.write({"is_default": True})
