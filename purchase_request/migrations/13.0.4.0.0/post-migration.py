from odoo import SUPERUSER_ID, api
from odoo.tools.sql import column_exists


def migrate(cr, version=None):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if column_exists(cr, "product_template", "purchase_request"):
        _migrate_purchase_request_to_property(env)


def _migrate_purchase_request_to_property(env):
    """Create properties for all products with the flag set on all companies"""
    env.cr.execute("select id, coalesce(purchase_request, False) from product_template")
    values = dict(env.cr.fetchall())
    for company in env["res.company"].with_context(active_test=False).search([]):
        env["ir.property"].with_context(force_company=company.id).set_multi(
            "purchase_request", "product.template", values, False,
        )
    env.cr.execute("alter table product_template drop column purchase_request")
