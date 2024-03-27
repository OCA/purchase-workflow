# Copyright 2021 Comunitea - Omar Castiñeira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Global Discount",
    "version": "14.0.1.0.0",
    "category": "Purchases Management",
    "author": "Comunitea, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["account_global_discount", "purchase"],
    "data": ["views/purchase_order_views.xml", "views/report_purchase_order.xml"],
    "application": False,
    "installable": True,
}
