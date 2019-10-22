# Copyright 2019 Eficent
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Supplierinfo for Customers Purchase",
    "summary": "Adds purchase manager permissions for customerinfo.",
    "version": "12.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/product-attribute",
    "category": "Purchase Management",
    "license": 'AGPL-3',
    "depends": [
        "purchase", "product_supplierinfo_for_customer",
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    'installable': True,
    'auto_install': True,
}
