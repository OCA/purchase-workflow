{
    "name": "Purchase Order Downpayment",
    "version": "16.0.1.0.0",
    "author": "Open Source Integrators (OSI), Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "license": "AGPL-3",
    "summary": "Allow to add payments from Purchase order view",
    "depends": ["purchase", "account"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_order_downpayment_wiz_view.xml",
        "views/purchase_view.xml",
    ],
    "installable": True,
}
