# Copyright 2020 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Supplier Calendar",
    "summary": "Supplier Calendar",
    "version": "13.0.1.0.0",
    "category": "Purchase Management",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["NuriaMForgeFlow"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "depends": ["purchase_stock", "resource"],
    "data": ["views/res_partner_view.xml", "views/product_view.xml"],
}
