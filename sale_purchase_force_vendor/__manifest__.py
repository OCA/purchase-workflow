# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Purchase Force Vendor",
    "version": "16.0.1.0.0",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale_purchase_stock"],
    "installable": True,
    "data": [
        "views/res_config_settings_view.xml",
        "views/sale_order_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
