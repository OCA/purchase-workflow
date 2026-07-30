# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Purchase Order Line Hide Description",
    "summary": """
        This module hide the description of the purchase order lines without
        hiding the sections and notes to avoid a redundant existing
        product field in the case when sale line description won't change
        by company policy.
        It will continue to appear in the reports.
    """,
    "version": "17.0.1.0.0",
    "category": "Purchases Management",
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "assets": {
        "web.assets_backend": [
            "purchase_order_line_hide_description/static/src/js/purchase_order_line_renderer.esm.js",
            "purchase_order_line_hide_description/static/src/css/purchase_order_line_renderer.css",
        ],
    },
    "installable": True,
}
