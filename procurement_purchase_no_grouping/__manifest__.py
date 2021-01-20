# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2017 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Procurement Purchase No Grouping',
    'version': '12.0.2.0.0',
    'author': 'AvanzOSC,'
              'Tecnativa,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/purchase-workflow',
    'category': 'Procurements',
    'depends': [
        'purchase_stock',
    ],
    'data': [
        'views/product_category_view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
