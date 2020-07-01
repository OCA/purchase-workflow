# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Purchase Price Recalculation',
    'summary': 'Allows to recompute purchase lines',
    'version': '12.0.1.0.0',
    "author": "Akretion,"
              "Odoo Community Association (OCA)",
    'category': 'Purchase Management',
    'license': 'AGPL-3',
    'website': "https://github.com/OCA/purchase-workflow",
    'depends': ['purchase'],
    'data': [
        'view/actions_server.xml'
    ],
    'installable': True,
}
