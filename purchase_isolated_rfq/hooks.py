# Copyright 2020 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import ast

from odoo import SUPERUSER_ID, api

ACTIONS = {
    "purchase.purchase_rfq": {"dom": [], "ctx": {"quotation_only": True}},
    "purchase.purchase_form_action": {
        "dom": [("state", "in", ("purchase", "done"))],
        "ctx": {},
    },
}


def post_init_hook(cr, registry):
    """ Set value for order_sequence on old records """
    cr.execute(
        """
        update purchase_order
        set order_sequence = true
        where state not in ('draft', 'cancel')
        """
    )


def uninstall_hook(cr, registry):
    """ Restore purchase.order action's domain/context """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for action_id in ACTIONS:
            action = env.ref(action_id)
            # Clean context
            ctx = ast.literal_eval(action.context)
            if "order_sequence" in ctx:
                del ctx["order_sequence"]
            if "default_order_sequence" in ctx:
                del ctx["default_order_sequence"]
            # Clean domain
            dom = ast.literal_eval(action.domain or "[]")
            dom = [x for x in dom if x[0] != "order_sequence"]
            # Assign original domain / context
            dom += ACTIONS[action_id]["dom"]
            dom = list(set(dom))
            ctx.update(ACTIONS[action_id]["ctx"])
            action.write({"context": ctx, "domain": dom})
