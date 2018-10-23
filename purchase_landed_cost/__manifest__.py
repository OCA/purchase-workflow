# -*- coding: utf-8 -*-
# Copyright 2013 Joaquín Gutierrez
# Copyright 2014-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

{
    'name': 'Purchase landed costs - Alternative option',
    'version': '10.0.2.0.0',
    "author": u"OdooMRP team,"
              u"AvanzOSC,"
              u"Tecnativa,"
              u"Joaquín Gutierrez,"
              u"Odoo Community Association (OCA)",
    'category': 'Purchase Management',
    'website': 'https://github.com/OCA/purchase-workflow',
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
        'views/purchase_cost_distribution_line_expense_view.xml',
        'views/purchase_expense_type_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_picking_view.xml',
        'data/purchase_cost_distribution_sequence.xml',
        'security/purchase_landed_cost_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'images': [
        '/static/description/images/purchase_order_expense_main.png',
        '/static/description/images/purchase_order_expense_line.png',
        '/static/description/images/expenses_types.png',
    ],
    'license': 'AGPL-3',
}
