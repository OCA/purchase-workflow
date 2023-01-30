# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase - Order Qty By Product Category",
    "version": "15.0.1.0.0",
    "category": "Purchase Management",
    "author": "Camptocamp, Odoo Community Association (OCA), Italo Lopes",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order.xml",
        "views/res_config_settings.xml",
    ],
    "depends": ["purchase"],
    "installable": True,
}
