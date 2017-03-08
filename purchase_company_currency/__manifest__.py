# -*- coding: utf-8 -*-
# Copyright Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Company currency in purchase orders",
    'version': "10.0.1.0.0",
    'author': "Camptocamp, "
              "Odoo Community Association (OCA) ",
    'website': "https://odoo-community.org/",
    'category': "Purchase",
    'license': "AGPL-3",
    'depends': ["purchase"],
    'data': [
        "views/purchase_order_view.xml"
    ],
    'installable': True,
}
