# Copyright 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Purchase order line description",
    "version": "19.0.1.0.1",
    "category": "Purchase Management",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "assets": {
        "web.assets_backend": [
            "purchase_order_line_description/static/src/js/purchase_product_field.esm.js",
        ],
        "web.assets_tests": [
            "purchase_order_line_description/static/tests/tours/*.js",
        ],
    },
}
