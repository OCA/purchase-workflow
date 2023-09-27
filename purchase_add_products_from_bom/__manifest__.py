# Copyright 2021 Akretion - www.akretion.com.br -
# @author  Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Purchase - Add Products from BoM',
    'version': '12.0.1.0.0',
    'author': 'Akretion,'
              'Odoo Community Association (OCA)',
    'category': 'Purchase Management',
    'license': 'AGPL-3',
    'depends': [
        'purchase_mrp',
    ],
    'website': 'https://github.com/OCA/purchase-workflow',
    'development_status': 'Mature',
    'maintainers': [
        'mbcosta',
    ],
    'data': [
        # Wizard
        'wizard/add_products_from_bom_view.xml',
        # Views
        'views/purchase_order_view.xml',
    ],
    'installable': True,
}
