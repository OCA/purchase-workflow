from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, pool):
    """
    Fetches all the PO and adds fields to the report.
    """
    env = Environment(cr, SUPERUSER_ID, {})
    purchase_order_records = env["purchase.order"].search([])
    purchase_order_records.add_report_fields()
