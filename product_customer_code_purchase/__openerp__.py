# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    "name": "Product Customer code for Purchase Order",
    "version": "8.0.1.0.0",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "website": "http://www.agilebg.com",
    "license": 'AGPL-3',
    "category": 'Purchase Management',
    "depends": [
        'product_customer_code',
        'purchase',
    ],
    "data": ['views/purchase_view.xml'],
    "installable": True,
}
