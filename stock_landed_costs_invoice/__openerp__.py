# -*- coding: utf-8 -*-
{
    'name': "WMS Landed Costs - Invoice",

    'summary': """
        allow to creating & grouping invoices per supplier of all
        selected landed costs.
""",

    'description': """
        TODO
    """,

    'author': "Elico Corp / Camptocamp",
    'website': "",

    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock_landed_costs'],

    'data': [
        # 'security/ir.model.access.csv',
        'wizard/generate_invoice_for_landed_costs_view.xml',
        'stock_landed_costs_invoice_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
