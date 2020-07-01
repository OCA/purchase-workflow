# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

{
    'name': "Purchase Request Product Usage",
    'version': '12.0.1.0.0',
    'category': 'Purchase Management',
    'author': "Eficent, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/purchase-workflow',
    'license': 'AGPL-3',
    "depends": [
        'purchase_request',
        'purchase_product_usage'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/purchase_request_view.xml',
        'wizards/purchase_request_line_make_purchase_order_view.xml',
    ],
    "installable": True
}
