# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Company Invoice Address",
    "summary": "Select the buying company's invoice address on purchase orders",
    "version": "16.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "data": [
        "views/purchase_order_views.xml",
        "views/account_move_views.xml",
        "reports/purchase_order_templates.xml",
    ],
    "maintainers": ["nobuQuartile"],
    "installable": True,
}
