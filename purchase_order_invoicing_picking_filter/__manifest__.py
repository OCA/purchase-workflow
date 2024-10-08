{
    "name": "Purchase Order Invoicing Picking Filter",
    "summary": "Create invoices from purchase orders based on the products in pickings.",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Sygel, Domatix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Invoicing",
    "depends": [
        "delivery",
        "purchase_stock",
        "sale_order_invoicing_picking_filter",
        "purchase_order_line_menu",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_invoicing_picking_filter_views.xml",
        "views/purchase_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
