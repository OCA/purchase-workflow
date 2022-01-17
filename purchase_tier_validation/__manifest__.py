# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Tier Validation",
    "summary": "Extends the functionality of Purchase Orders to "
    "support a tier validation process.",
    "version": "14.0.2.0.1",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase", "base_tier_validation"],
    "data": ["views/purchase_order_view.xml"],
}
