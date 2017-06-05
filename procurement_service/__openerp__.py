# -*- coding: utf-8 -*-
# Copyright 2015 Avanzosc(http://www.avanzosc.es)
# Copyright 2015 Tecnativa (http://www.tecnativa.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Procurement Service",
    "version": "8.0.1.0.0",
    "summary": "Allows to generate procurements from confirmed sale orders",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Tecnativa",
    "website": "http://www.odoomrp.com",
    "category": "Procurements",
    "depends": ['product',
                'sale',
                'stock',
                'purchase',
                ],
    "data": ['views/product_template_view.xml',
             ],
    "installable": True
}
