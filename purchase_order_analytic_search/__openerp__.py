# -*- coding: utf-8 -*-
# © 2015-17 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Purchase Order Analytic Search",
    "summary": """
        Search purchase orders by analytic account. New menu entry in
        Purchasing to list purchase order lines.
        """,
    "version": "9.0.1.0.0",
    "website": "https://odoo-community.org/",
    "category": "Purchase Workflow",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["analytic", "purchase"],
    "data": ["views/purchase_order_view.xml"],
}
