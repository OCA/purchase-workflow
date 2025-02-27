from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Allow all purchase managers to set orders to force invoiced"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref("purchase.group_purchase_manager").implied_ids += env.ref(
        "purchase_force_invoiced.group_force_invoiced"
    )
