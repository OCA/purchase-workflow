# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Vendor transport lead time",
    "summary": "Purchase delay based on transport and supplier delays",
    "version": "13.0.1.2.0",
    "website": "https://odoo-community.org/",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["product", "purchase"],
    "data": [
        "views/product_supplierinfo.xml",
        "views/purchase_order_line.xml",
        "report/purchase_order_template.xml",
    ],
    "installable": True,
}
