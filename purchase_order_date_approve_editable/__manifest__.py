# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Purchase Order Date Approve Editable",
    "summary": """
        Allows editing the Approval Date on Purchase Orders
    """,
    "author": "Solvos," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "version": "17.0.1.0.0",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_views.xml",
    ],
    "installable": True,
}
