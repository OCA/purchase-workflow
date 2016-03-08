# -*- coding: utf-8 -*-
# © 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Discounts in product supplier info",
    "version": "9.0.1.0.0",
    "author": "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Antiun Ingeniería S.L., "
              "Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "website": "www.serviciosbaeza.com",
    "license": "AGPL-3",
    "depends": [
        'product',
        'purchase_discount',
    ],
    "data": [
        'views/product_supplierinfo_view.xml',
    ],
    'installable': True,
}
