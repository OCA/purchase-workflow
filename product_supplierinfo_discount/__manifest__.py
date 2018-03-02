# -*- coding: utf-8 -*-
# © 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# © 2016 GRAP (http://www.grap.coop)
#        Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Discounts in product supplier info",
    "version": "10.0.1.0.0",
    "author": "Tecnativa, "
              "GRAP, "
              "Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "website": "http://www.serviciosbaeza.com/",
    "license": "AGPL-3",
    "depends": [
        'product',
        'purchase_discount',
    ],
    "data": [
        'views/product_supplierinfo_view.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
}
