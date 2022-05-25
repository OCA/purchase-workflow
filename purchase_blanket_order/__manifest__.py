# Copyright (C) 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Blanket Orders",
    "category": "Purchase",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "13.0.2.0.0",
    "website": "https://github.com/OCA/purchase-workflow",
    "summary": "Purchase Blanket Orders",
    "depends": ["purchase", "web_action_conditionable"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/sequence.xml",
        "data/ir_cron.xml",
        "wizard/create_purchase_orders.xml",
        "views/purchase_config_settings.xml",
        "views/purchase_blanket_order_views.xml",
        "views/purchase_order_views.xml",
        "report/templates.xml",
        "report/report.xml",
    ],
    "installable": True,
}
