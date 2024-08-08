# Copyright 2024 Raumschmiede GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

{
    "name": "Purchase Line Service Qty Received",
    "summary": "Changes the Received Quantity (qty_received) of a service purchase.order.line"
    "if one other purchase.order.line is received the qty_received of the service line"
    "is changed to its Quantity (product_uom_qty)",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "author": "Raumschmiede GmbH, MT Software, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase_stock",
    ],
}
