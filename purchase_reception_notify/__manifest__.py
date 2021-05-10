# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

{
    "name": "Purchase Reception Notify",
    "version": "14.0.1.0.0",
    "category": "Purchase Management",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase_stock"],
    "data": ["data/mail.xml"],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
