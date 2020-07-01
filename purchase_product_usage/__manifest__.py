# Copyright 2019 Aleph Objects, Inc.
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

{
    'name': "Purchase Product Usage",
    'version': '12.0.1.0.0',
    'category': 'Purchase Management',
    'author': "Eficent, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/purchase-workflow',
    'license': 'AGPL-3',
    "depends": [
        'purchase',
    ],
    "data": [
        'security/purchase_product_usage.xml',
        'security/ir.model.access.csv',
        'views/purchase_order_line_view.xml',
        'views/purchase_product_usage_view.xml',
    ],
    "installable": True
}
