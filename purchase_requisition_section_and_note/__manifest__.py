# Copyright 2025 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Requisition Section and Note",
    "summary": "Add section and note to purchase requisition",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["bealdav"],
    "development_status": "Alpha",
    "license": "AGPL-3",
    "depends": [
        "purchase_requisition",
    ],
    "data": [
        "views/requisition.xml",
        "views/purchase.xml",
    ],
    "demo": ["data/demo.xml"],
    "installable": True,
}
