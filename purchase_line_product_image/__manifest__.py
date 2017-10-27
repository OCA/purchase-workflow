{
    "name": "Purchase Order Line Product Image",
    "summary": "Show Product Image at Purchase Order Line.",
    "version": "10.0.1.0.0",
    "author": "Lucky Kurniawan, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchases",
    "depends": ['purchase','web_tree_image'],
    "data": [
        # web_tree_image by OCA web
        'views/purchase_order_views.xml',
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
