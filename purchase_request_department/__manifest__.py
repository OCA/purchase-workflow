# Copyright 2017-2020 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Request Department",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "14.0.1.0.0",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "post_init_hook": "post_init_hook",
    "depends": ["hr", "purchase_request"],
    "data": ["views/purchase_request_department_view.xml"],
    "license": "AGPL-3",
    "installable": True,
}
