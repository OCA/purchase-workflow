# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Purchase Force Vendor",
    "version": "14.0.2.0.0",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale_purchase_stock", "web_domain_field"],
    "installable": True,
    "data": [
        "views/res_config_settings_view.xml",
        "views/sale_order_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
