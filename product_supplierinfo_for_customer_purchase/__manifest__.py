# Copyright 2021 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    "name": "Product Customer code for purchase order",
    "version": "14.0.1.0.0",
    "summary": "Loads in every purchase order the customer code defined in the product",
    "author": "Agile Business Group,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "category": "Purchases",
    "depends": [
        "purchase",
        "product_supplierinfo_for_customer",
    ],
    "data": ["views/purchase_view.xml"],
    "installable": True,
}
