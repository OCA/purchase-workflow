# -*- coding: utf-8 -*-
# Copyright 2013 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright 2015 Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase order revisions",
    "version": "10.0.1.0.0",
    "category": "Purchase Management",
    "author": "Agile Business Group,"
              "Camptocamp,"
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "http://www.agilebg.com",
    "license": "AGPL-3",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
