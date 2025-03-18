# Copyright 2019-2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Request Tier Validation",
    "summary": "Extends the functionality of Purchase Requests to "
    "support a tier validation process.",
    "version": "17.0.1.1.1",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_request", "base_tier_validation"],
    "data": [
        "views/purchase_request_view.xml",
    ],
    "demo": [
        "demo/tier_definition.xml",
    ],
}
