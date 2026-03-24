# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Order Line Copier",
    "version": "19.0.1.0.0",
    "category": "Purchase",
    "summary": "Duplicate purchase order lines with a single click",
    "author": "Heliconia Solutions Pvt. Ltd., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/copy_purchase_line_wizard_views.xml",
        "views/purchase_order_line_views.xml",
        "data/server_actions.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "purchase_order_line_copier/static/src/js/copy_pol_header.esm.js",
        ],
    },
    "development_status": "Beta",
    "maintainers": ["Bhavesh Heliconia"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
