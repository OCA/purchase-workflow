# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Purchase Order Line Description Without Product Code",
    "summary": """
        Avoid duplicated product codes in purchase order line descriptions
    """,
    "author": "Solvos," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "version": "18.0.1.0.0",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
    "installable": True,
}
