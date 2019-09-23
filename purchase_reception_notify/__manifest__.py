# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

{
    'name': "Purchase Reception Notify",
    'version': '12.0.1.0.0',
    'category': 'Purchase Management',
    'author': "Eficent, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/purchase-workflow',
    'license': 'AGPL-3',
    "depends": [
        'purchase_stock',
    ],
    "data": ["data/mail.xml",
             ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
