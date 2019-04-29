# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase Merge',
    'summary': 'Wizard to merge purchase with required conditions',
    'version': '11.0.1.1.0',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Purchase',
    'depends': [
        'purchase',
    ],
    'data': [
        'wizard/purchase_merge_views.xml',
    ],
    'installable': True,
}
