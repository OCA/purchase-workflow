# -*- coding: utf-8 -*-
# Copyright 2015 OdooMRP team
# Copyright 2015 AvanzOSC
# Copyright 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Products Menu",
    "version": "9.0.1.0.0",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "Eficent Business and IT Consulting Services S.L.,"
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Daniel Campos <danielcampos@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Jordi Ballester Alomar <jordi.ballester@eficent.com>",
    ],
    "depends": [
        "purchase",
        "product",
    ],
    "category": "Hidden/Dependency",
    "data": [
        "views/purchase_order_view.xml"
    ],
    "installable": True,
    "auto_install": True,
}
