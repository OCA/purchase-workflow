# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Receipt Threshold",
    "version": "17.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Inventory/Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        # odoo
        "purchase_stock",
    ],
    "data": [
        "views/purchase_order.xml",
        "views/purchase_order_line.xml",
        "views/res_config_settings.xml",
        "views/res_partner.xml",
    ],
}
