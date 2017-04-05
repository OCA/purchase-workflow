# -*- coding: utf-8 -*-
# Copyright 2015-17 Eficent Business and IT Consulting Services, S.L.
#           (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Supplier Code in Purchase",
    "summary": "This module adds to the purchase order line the supplier "
               "code defined in the product.",
    "version": "9.0.1.0.0",
    "author": "Eficent, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Purchase Management",
    "depends": ["purchase"],
    "license": "AGPL-3",
    "data": [
        "views/purchase_order_view.xml",
    ],
    'installable': True,
}
