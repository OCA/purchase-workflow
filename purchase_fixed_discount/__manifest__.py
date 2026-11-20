# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Fixed Discount",
    "summary": "Allows to apply fixed amount discounts in purchase orders.",
    "version": "18.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["purchase", "account_invoice_fixed_discount"],
    "data": [
        "views/purchase_order_views.xml",
    ],
}
