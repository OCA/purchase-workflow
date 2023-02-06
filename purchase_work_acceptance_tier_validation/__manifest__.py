# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Work Acceptance Tier Validation",
    "summary": "Extends the functionality of Work Acceptance to "
    "support a tier validation process.",
    "version": "15.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["kittiu"],
    "depends": ["purchase_work_acceptance", "base_tier_validation"],
    "data": ["views/work_acceptance_view.xml"],
}
