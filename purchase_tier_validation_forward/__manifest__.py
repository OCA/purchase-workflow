# Copyright 2020 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Tier Validation - Forward Option",
    "version": "13.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["base_tier_validation_forward", "purchase_tier_validation"],
    "data": ["views/purchase_order_view.xml"],
}
