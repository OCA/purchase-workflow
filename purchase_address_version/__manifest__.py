# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Address Version",
    "summary": "Custom exceptions on purchase order",
    "version": "14.0.1.0.0",
    "category": "Generic Modules/Purchase",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase", "partner_address_version"],
    "license": "AGPL-3",
    "data": [
        "views/purchase_view.xml",
    ],
    "maintainers": ["kittiu"],
    "installable": True,
}
