# Copyright 2023 Moduon - Andrea Cattalani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl
{
    "name": "Purchase requisition analytic",
    "summary": "Add analytic account in RFQ lines",
    "version": "14.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["shide", "anddago78"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "analytic",
        "purchase_requisition",
    ],
    "data": [],
}
