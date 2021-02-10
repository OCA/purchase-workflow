# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Agreements Tier Validation",
    "summary": "Extends the functionality of Purchase Agreements to "
    "support a tier validation process.",
    "version": "14.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_requisition", "base_tier_validation"],
    "data": ["views/purchase_requisition_view.xml"],
}
