# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Report Date Planned",
    "version": "14.0.1.1.0",
    "author": "Akretion ,Odoo Community Association (OCA)",
    "maintainers": ["mathieudelva"],
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_usability",
    ],
    "data": [
        "views/purchase_report.xml",
    ],
}
