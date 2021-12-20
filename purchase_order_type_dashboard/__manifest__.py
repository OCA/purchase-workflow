# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Order Type Dashboard",
    "version": "13.0.1.0.0",
    "author": "Solvos, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Purchase Management",
    "depends": ["purchase_order_type"],
    "website": "https://github.com/OCA/purchase-workflow",
    "data": [
        "views/view_purchase_order.xml",
        "views/view_purchase_order_type.xml",
        "views/menu_purchase_order.xml",
    ],
    "maintainers": ["dalonsod"],
    "installable": True,
    "auto_install": False,
}
