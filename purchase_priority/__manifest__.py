# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Priority',
    'summary': """Priority Star on Purchase Orders""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/purchase-workflow',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_order.xml',
    ],
}
