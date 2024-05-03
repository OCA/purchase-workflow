# Copyright 2020 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Supplier Calendar",
    "summary": "Supplier Calendar",
    "version": "17.0.1.0.0",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["LoisRForgeFlow"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "depends": ["purchase_stock", "resource"],
    "data": ["views/res_partner_view.xml", "views/product_view.xml"],
}
