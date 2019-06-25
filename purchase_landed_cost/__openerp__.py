# -*- coding: utf-8 -*-
# © 2013 Joaquín Gutierrez
# © 2014-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3


{
    'name': 'Purchase landed costs - Alternative option',
    'version': '8.0.2.3.0',
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "Tecnativa,"
              "Joaquín Gutierrez",
    'category': 'Purchase Management',
    'website': 'http://www.odoomrp.com',
    'summary': 'Purchase cost distribution',
    'depends': [
        'stock',
        'purchase',
    ],
    'data': [
        'wizard/picking_import_wizard_view.xml',
        'wizard/import_invoice_line_wizard_view.xml',
        'wizard/import_landed_cost_pickings_wizard_view.xml',
        'views/account_invoice_view.xml',
        'views/purchase_cost_distribution_view.xml',
        'views/purchase_expense_type_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_picking_view.xml',
        'data/purchase_cost_distribution_sequence.xml',
        'security/purchase_landed_cost_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': False,
    'images': [
        '/static/description/images/purchase_order_expense_main.png',
        '/static/description/images/purchase_order_expense_line.png',
        '/static/description/images/expenses_types.png',
    ],
}
