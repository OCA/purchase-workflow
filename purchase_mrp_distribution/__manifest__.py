# Copyright 2024 Tecnatva - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase MRP Distribution",
    "version": "15.0.1.0.0",
    "author": "Tecnaiva, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchases",
    "depends": ["purchase_mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_bom_views.xml",
        "views/stock_picking_views.xml",
        "wizards/stock_move_distribution_wiz_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
