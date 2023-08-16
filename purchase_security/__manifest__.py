# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Order security",
    "version": "16.0.1.0.0",
    "category": "Purchase",
    "development_status": "Production/Stable",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "summary": "See only your purchase orders",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "maintainers": ["pilarvargas-tecnativa"],
    "data": ["security/security.xml", "views/purchase_order_views.xml"],
    "installable": True,
    "auto_install": False,
}
