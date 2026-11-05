# Copyright 2025 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Hide Price",
    "summary": "Hide price for specific group and vendor",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": [
        "bealdav",
    ],
    "development_status": "Alpha",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "data": [
        "security/security.xml",
        "views/partner.xml",
        "views/purchase.xml",
    ],
    "installable": True,
}
