# Copyright (C) 2022 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Purchase Data Freight",
    "version": "14.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "maintainers": [
        "bealdav",
        "hparfr",
    ],
    "summary": "Manage goods take off with total delay",
    "depends": [
        "purchase_partner_incoterm",
        "onchange_helper",
    ],
    "data": [
        "views/freight_rule.xml",
        "views/purchase.xml",
        "views/picking.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "data/freight.rule.csv",
        "data/demo.xml",
    ],
}
