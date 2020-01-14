
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Product Last Price Info - Purchase",
    "version": "11.0.1.0.1",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Carlos Lopez Mite <celm1990@hotmail.com>",
        "Adria Gil Sorribes <adria.gil@eficent.com>",
    ],
    "depends": [
        "purchase",
    ],
    "data": [
        "views/product_views.xml",
    ],
    "installable": True,
    "post_init_hook": "set_last_price_info",
}
