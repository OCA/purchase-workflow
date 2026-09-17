# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Flag, per company, the order type _default_order_type() used to
    return before is_default existed: the lowest-sequence type in that
    company's scope. Only existing installations need this - a fresh
    install has nothing configured and simply leaves order_type empty
    until a default is set, which is the intended behavior going forward.
    """
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    order_type = env["purchase.order.type"]

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
