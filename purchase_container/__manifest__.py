{
    "name": "purchase_container",
    "summary": """Add containers to purchase orders and stock pickings.""",
    "version": "14.0.1.0.0",
    "license": "",
    "author": "Florian Mounier",
    "website": "https://gitlab.akretion.com/akretion/noukies-modules",
    "depends": [
        "purchase_stock",
    ],
    "data": [
        "views/purchase_views.xml",
        "views/purchase_container_views.xml",
        "views/stock_picking_views.xml",
        "security/ir.model.access.csv",
    ],
}
