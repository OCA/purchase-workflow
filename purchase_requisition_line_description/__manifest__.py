# Copyright 2021 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Requisition Line Description',
    'summary': 'Extends the functionality of Purchase Agreements to '
               'show line description.',
    'version': '12.0.1.0.0',
    'category': 'Purchases',
    'website': 'https://github.com/OCA/purchase-workflow',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'purchase_requisition',
    ],
    'data': [
        'views/purchase_requisition.xml',
        'report/purchase_requisition_report.xml',
    ],
}
