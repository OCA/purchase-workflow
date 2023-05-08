# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Restriction",
    "version": "16.0.1.0.0",
    "author": "Quartile Limited, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "data": [
        "views/purchase_views.xml",
        "security/security.xml",
    ],
    "installable": True,
}
