# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Auto Validation",
    "summary": "Purchase Auto Validation with rules",
    "version": "14.0.1.0.0",
    "category": "purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["Kev-Roche"],
    "application": False,
    "installable": True,
    "depends": [
        "purchase_stock",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "views/purchase_order.xml",
        "views/purchase_auto_validation.xml",
        "security/ir.model.access.csv",
    ],
}
