# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Purchase Auto Lock",
    "version": "13.0.1.0.0",
    "category": "Purchase",
    "summary": "Lock Fully Received and Invoiced POs",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["purchase_stock"],
    "data": ["data/purchase_order.xml", "views/res_config_settings_view.xml"],
}
