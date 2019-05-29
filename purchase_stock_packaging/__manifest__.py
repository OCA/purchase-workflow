# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Stock Packaging',
    'summary': """
        Adds the ability to manage product packaging
        with purchase and stock""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'depends': [
        'purchase_stock',
        'purchase_packaging',
    ],
    'installable': True,
    'auto_install': True,
}
