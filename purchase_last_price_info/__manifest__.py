# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Purchase Product Last Price Info",
    "version": "14.0.1.0.0",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
    "AvanzOSC, "
    "Tecnativa - Pedro M. Baeza, "
    "Odoo Community Association (OCA)",
    "development_status": "Beta",
    "maintainers": ["LoisRForgeFlow"],
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": ["views/product_views.xml"],
    "installable": True,
    "post_init_hook": "set_last_price_info",
}
