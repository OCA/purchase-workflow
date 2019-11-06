# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
{
    'name': 'Purchase Stock Secondary Unit',
    'summary': 'Propagate secondary UoM from PO lines to Stock Moves',
    'version': '12.0.1.0.0',
    'development_status': 'Alpha',
    'category': 'Purchase',
    'website': 'https://github.com/OCA/purchase-workflow',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': True,
    'depends': [
        'stock_secondary_unit',
        'purchase_secondary_unit',
    ],
}
