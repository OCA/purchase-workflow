# Copyright 2019 RGB Consulting - Domantas Sidorenkovas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase Supplier Approve',
    'version': '12.0.1.0.0',
    'category': 'Purchase',
    'depends': ['purchase'],
    'author': 'RGB Consulting, '
              'Odoo Community Association (OCA)',
    'maintainers': ['admin-rgbconsulting'],
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/purchase-workflow',
    'data': [
        'security/purchase_security.xml',
        'views/res_partner_view.xml',
        'wizard/supplier_approval_wizard.xml',
    ],

}
