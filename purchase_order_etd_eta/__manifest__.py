# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order ETD/ETA",
    "summary": "Add Estimated Time of Departure/Arrival fields to Purchase Orders",
    "version": "18.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Quartile, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "data": [
        "report/purchase_order_templates.xml",
        "report/purchase_quotation_templates.xml",
        "views/purchase_order_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
