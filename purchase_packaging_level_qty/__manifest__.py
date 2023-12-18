{
    "name": "Purchase Packaging Level Quantity",
    "summary": """Display purchase order packaging level quantity""",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "depends": [
        "purchase",
        "product_packaging_level",
    ],
    "data": [
        "views/purchase_order_view.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
