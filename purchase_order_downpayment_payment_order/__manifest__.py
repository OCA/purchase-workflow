{
    "name": "Purchase Order Downpayment to payment order",
    "version": "16.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "license": "AGPL-3",
    "summary": "Allow to add payments to payment order from Purchase order view",
    "depends": [
        "purchase_order_downpayment",
        "account_payment_order",
        "account_payment_mode",
    ],
    "data": [
        "wizard/purchase_order_downpayment_wiz_view.xml",
    ],
    "installable": True,
}
