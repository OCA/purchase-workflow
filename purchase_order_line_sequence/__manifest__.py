# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Order Line Sequence",
    "summary": "Propagates PO line sequence to invoices and stock picking.",
    "version": "11.1.1.0.0",
    "author": "Eficent, "
              "Serpent CS, "
              "Odoo Community Association (OCA)",
    "category": "Purchase",
    "website": "https://www.eficent.com/",
    "license": "AGPL-3",
    'data': [
        'views/purchase_view.xml',
        'views/report_purchaseorder.xml',
    ],
    "depends": [
        "purchase",
    ],
    'post_init_hook': 'post_init_hook',
    "installable": True,
}
