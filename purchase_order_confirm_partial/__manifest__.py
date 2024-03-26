# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Partial Confirmation",
    "summary": "Select purchase order lines to be confirmed",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchases",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "wizard/purchase_order_confirm_partial_views.xml",
    ],
    "installable": True,
}
