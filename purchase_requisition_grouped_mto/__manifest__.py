# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase Requisition Grouped Mto',
    'summary': 'Group more than one sale order to a purchase requisition',
    'version': '11.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Purchase',
    'website': 'https://github.com/OCA/purchase-workflow',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'purchase_requisition',
    ],
    'data': [
        'views/product_views.xml',
    ],
}
