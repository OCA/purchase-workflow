# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Reqeust Exception",
    "summary": "Custom exceptions on purchase request",
    "version": "14.0.1.0.0",
    "category": "Generic Modules/Purchase",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_request", "base_exception"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/purchase_request_exception_data.xml",
        "wizard/purchase_request_exception_confirm_view.xml",
        "views/purchase_request_view.xml",
    ],
    "installable": True,
}
