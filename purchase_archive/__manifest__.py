# Copyright 2018 brain-tec AG - Raúl Martín
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Archive",
    "summary": "Allows to archive Purchase Orders in state draft, done or "
               "cancelled, and removes rights to delete them.",
    "version": "11.0.1.0.0",
    "development_status": "Beta",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "brain-tec AG,"
              "Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    "application": False,
    'installable': True,
    "depends": [
        "purchase"
    ],
    "data": ['views/purchase_order.xml',
             'security/ir.model.access.csv'
             ],
}
