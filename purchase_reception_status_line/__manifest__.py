# Copyright 2024 ForgeFlow (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Reception Status Line",
    "version": "15.0.2.0.0",
    "category": "Purchases",
    "license": "AGPL-3",
    "summary": "Add reception status on purchase order lines",
    "author": "ForgeFlow,Odoo Community Association (OCA)",
    "maintainers": ["DavidJForgeFlow"],
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_reception_status"],
    "data": [
        "views/purchase_order.xml",
        "views/purchase_order_line_views.xml",
    ],
    "installable": True,
}
