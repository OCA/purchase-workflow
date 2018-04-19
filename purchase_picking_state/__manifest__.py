# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Purchase Picking State',
    'summary': 'Add the status of all the incoming picking \n in the purchase order',
    'version': '11.0.1.0.0',
    'category': 'Purchase Management',
    'website': 'http://akretion.com',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_view.xml',
    ]
}
