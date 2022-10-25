# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order General Discount",
    "summary": "General discount per purchase order",
    "version": "14.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_discount"],
    "data": [
        "views/purchase_order_view.xml",
        "views/res_partner_view.xml",
        "views/res_config_view.xml",
    ],
}
