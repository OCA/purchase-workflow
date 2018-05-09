# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Tier Validation",
    "summary": "Extends the functionality of Purchase Orders to "
               "support a tier validation process.",
    "version": "11.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase",
        "base_tier_validation",
    ],
    "data": [
        "views/purchase_order_view.xml",
    ],
}
