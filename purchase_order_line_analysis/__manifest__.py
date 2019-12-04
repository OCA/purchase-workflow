# Copyright 2019 Openforce Srls Unipersonale (www.openforce.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase Orders Lines - Analysis',
    'summary': "Direct access to purchase order lines",
    'version': '12.0.1.0.0',
    "development_status": "Beta",
    'category': 'Purchase',
    'website': 'https://github.com/OCA/purchase-workflow',
    'author': 'Openforce, Odoo Community Association (OCA)',
    "maintainers": ['openforceit'],
    'license': 'AGPL-3',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_views.xml',
    ],
}
