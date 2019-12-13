# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Manual Delivery',
    'summary': """
        Prevents pickings to be auto generated upon Purchase Order confirmation
        and adds the ability to manually generate them as the supplier confirms
        the different purchase order lines.
    """,
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ForgeFlow S.L.,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/purchase-workflow',
    'depends': [
        'purchase_stock'
    ],
    'data': [
        'wizard/create_manual_stock_picking.xml',
        'views/purchase_order_views.xml',
    ],
}
