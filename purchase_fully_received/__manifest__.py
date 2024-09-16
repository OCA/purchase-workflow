# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Purchase Fully Received",
    "summary": "Useful filters in Purchases to know the actual status of shipments."
    "and invoices",
    "author": "Forgeflow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "version": "16.0.1.0.0",
    "depends": [
        "purchase_stock",
    ],
    "data": [
        "views/purchase_views.xml",
    ],
    "installable": True,
}
