# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Purchase - Multi branch",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "category": "Purchase Management",
    "summary": "Add branch on Purchase",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase", "account_multi_branch"],
    "data": [
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
}
