# -*- coding: utf-8 -*-
{
    'name': "WMS Landed Costs - Multi Currency",

    'summary': """
        support secondary currency on the landed cost line.
""",

    'description': """
        TODO
    """,

    'author': "Elico Corp / Camptocamp",
    'website': "",

    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock_landed_costs_invoice'],

    'data': [
        'stock_landed_costs_multi_currency_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
