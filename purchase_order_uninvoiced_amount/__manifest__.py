# Copyright 2020 Tecnativa - Manuel Calero
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Purchase Order Univoiced Amount",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "version": "12.0.2.0.1",
    'development_status': 'Beta',
    "website": "https://github.com/OCA/purchase-workflow",
    'category': 'Purchase',
    'license': 'AGPL-3',
    'application': False,
    "installable": True,
    'depends': [
        'purchase',
    ],
    "data": [
        'views/purchase_order_view.xml',
    ],
}
