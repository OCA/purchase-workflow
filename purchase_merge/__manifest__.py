# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Merge",
    "summary": "Wizard to merge purchase with required conditions",
    "version": "16.0.1.0.1",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "category": "Purchase",
    "depends": ["purchase_order_approved"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_merge_views.xml",
    ],
    "external_dependencies": {"python": ["openupgradelib"]},
    "installable": True,
}
