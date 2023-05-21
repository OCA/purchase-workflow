from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, pool):
    """
    Fetches all the PO and adds fields to the report.
    """
    env = Environment(cr, SUPERUSER_ID, {})
    purchase_order_records = env["purchase.order"].search([])
    po_report_template = env["po.line.report.template"].create(
        {
            "name": "Template 1",
            "report_field_ids": env["purchase.report.field"].generate_data(),
        }
    )
    purchase_order_records.write({"po_line_report_template_id": po_report_template.id})
