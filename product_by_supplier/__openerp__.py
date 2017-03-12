# -*- coding: utf-8 -*-
# (c) 2010-2013 Elio Corp. - LIN Yu
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Product by supplier info',
    'version': '9.0.1.0.0',
    'category': 'purchase',
    'summary': 'Show products grouped by suppliers',
    'author': "Elico Corp, "
              "Camptocamp SA, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.elico-corp.com,',
    'license': 'AGPL-3',
    'depends': [
        'product',
        'purchase',
    ],
    'data': [
        'views/product_supplierinfo_view.xml',
    ],
    'installable': True,
}
