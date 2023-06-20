# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Purchase Request - Multi branch",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "category": "Purchase Management",
    "summary": "Add branch on Purchase Request",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_request", "purchase_multi_branch"],
    "data": [
        "views/purchase_request_views.xml",
        "wizard/purchase_request_line_make_purchase_order_view.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
}
