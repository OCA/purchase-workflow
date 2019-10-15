# Copyright 2019 Ecosoft Co., Ltd., Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Purchase Invoice Plan & Deposit',
    'version': '12.0.1.0.0',
    'summary': 'Bridge module for purchase_invoice_plan and purchase_deposit',
    'author': 'Ecosoft, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/purchase-workflow',
    'category': 'Purchase Management',
    'license': 'AGPL-3',
    'depends': [
        'purchase_deposit',
        'purchase_invoice_plan',
    ],
    'installable': True,
    'auto_install': True,
}
