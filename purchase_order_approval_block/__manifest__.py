# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Purchase Order Approval Block",
    "author": "Eficent, Odoo Community Association (OCA)",
    "version": "12.0.1.0.0",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        'purchase_stock',
        'purchase_exception',
    ],
    "data": [
        'data/purchase_exception_data.xml',
        'security/ir.model.access.csv',
        'security/purchase_order_approval_block_security.xml',
        'views/purchase_approval_block_reason_view.xml',
        'views/purchase_order_view.xml',
    ],
    "license": 'LGPL-3',
    "installable": True
}
