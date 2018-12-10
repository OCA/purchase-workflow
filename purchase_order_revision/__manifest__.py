# Copyright 2013 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright 2015 Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2018 Ramon Bajona <ramon.bajona@guadaltech.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase order revisions",
    "version": "11.0.1.0.0",
    "category": "Purchase Management",
    "author": "Agile Business Group, "
              "Camptocamp, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow/tree/11.0/purchase_order_revision",
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
