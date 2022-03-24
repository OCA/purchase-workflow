# Copyright 2022 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Order Line Initial Quantity",
    "summary": "Allows to display the initial quantity when the quantity "
    "has been modified on the purchase line.",
    "version": "14.0.1.0.0",
    "category": "Inventory/Purchase",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "data": [
        "views/purchase.xml",
    ],
    "installable": True,
}
