# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Purchase Requisition Stock Dropshipping",
    "version": "17.0.1.0.0",
    "author": "Odoo Community Association (OCA), Odoo SA",
    "category": "Purchases",
    "summary": "Purchase Requisition, Stock, Dropshipping",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["stock_dropshipping", "procurement_purchase_requisition_generation"],
    "data": [
        "views/purchase_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
    "maintainers": ["carlos-lopez-tecnativa"],
}
