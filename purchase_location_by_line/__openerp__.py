# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (<http://www.eficent.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Location by Line",
    "summary": "Allows to define a specific destination location on each PO "
               "line",
    "version": "9.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": [
        "purchase",
        "purchase_delivery_split_date"
    ],
    "license": "AGPL-3",
    "data": [
        "views/purchase_view.xml"
    ],
    'installable': True,
}
