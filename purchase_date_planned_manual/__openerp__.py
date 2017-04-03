# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Date Planned Manual",
    "summary": "This module makes the system to always respect the planned "
               "(or scheduled) date in PO lines.",
    "version": "9.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Purchases",
    "depends": ["purchase"],
    "data": [
        'views/purchase_order_view.xml',
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
