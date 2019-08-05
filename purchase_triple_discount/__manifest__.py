# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Invoice Triple Discount',
    'version': '11.0.1.0.0',
    'category': 'Purchase Management',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/purchase-workflow',
    'license': 'AGPL-3',
    'summary': 'Manage triple discount on purchase order lines',
    'depends': [
        'product_supplierinfo_discount',
        'account_invoice_triple_discount',
    ],
    'data': [
        'views/product_supplierinfo_view.xml',
        'views/purchase_view.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
}
