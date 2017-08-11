# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Purchase Order Approval Block",
    "author": "Eficent, SerpentCS, Odoo Community Association (OCA)",
    "version": "10.0.1.0.0",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        'purchase',
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/purchase_order_approval_block_security.xml',
        'views/purchase_approval_block_reason_view.xml',
        'views/purchase_order_view.xml',
    ],
    "license": 'LGPL-3',
    "installable": True
}
