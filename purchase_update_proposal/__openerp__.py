# -*- coding: utf-8 -*-
# Copyright 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Update Proposal",
    "summary": "Allow to define alternate quantity, date on lines",
    "version": "8.0.0.1.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "depends": [
        "purchase",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/purchase_order.xml",
        "views/purchase_line_proposal.xml",
        "views/supplier_purchase_order.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["bealdav"],
}
