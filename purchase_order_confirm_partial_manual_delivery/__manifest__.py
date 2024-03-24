# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Partial Confirmation Manual Delivery",
    "summary": """
        Connect partial order confirmation
        and manual delivery modules to
        fix incompatibility issues.
    """,
    "author": "Cetmix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchases",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["purchase_order_confirm_partial", "purchase_manual_delivery"],
    "auto_install": True,
    "installable": True,
}
