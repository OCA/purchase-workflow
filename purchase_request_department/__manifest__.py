# Copyright 2017-2020 Forgeflow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Request Department",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "13.0.1.0.0",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "post_init_hook": "post_init_hook",
    "depends": ["hr", "purchase_request"],
    "data": ["views/purchase_request_department_view.xml"],
    "license": "LGPL-3",
    "installable": True,
}
