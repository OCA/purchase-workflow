# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Purchase Request Employee",
    "summary": "Allow to define employee that needs the purchase request",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "maintainers": ["alan196"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_request",
        "hr",
    ],
    "data": [
        "views/purchase_request_view.xml",
        "views/purchase_order_view.xml",
    ],
}
