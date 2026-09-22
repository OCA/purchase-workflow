{
    "name": "Purchase Order Line Merge",
    "version": "18.0.1.0.0",
    "author": "SpearHead, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "category": "Inventory/Purchase",
    "summary": "Merge purchase order lines into a new purchase order",
    "depends": ["purchase_order_line_menu", "purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_order_line_merge_views.xml",
    ],
    "installable": True,
}
