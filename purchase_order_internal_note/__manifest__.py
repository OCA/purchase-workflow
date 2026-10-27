# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Internal Note",
    "version": "19.0.1.0.0",
    "summary": """
        Adds new field Internal Note to the purchase order.
        It will not be included in the report.
    """,
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "category": "Purchase",
    "depends": ["purchase"],
    "data": ["views/purchase_order_views.xml"],
}
