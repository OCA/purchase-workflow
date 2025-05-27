# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Split Route",
    "summary": """""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "maintainers": ["mathieudelva"],
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase_stock",
        "sale_order_global_stock_route",
        "stock_mts_mto_rule",
    ],
    "data": ["views/stock_route.xml"],
}
