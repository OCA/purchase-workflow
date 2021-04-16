# Copyright 2023 François Poizat @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Update Proposal Group Backend",
    "summary": "Allow group backend user to use make purchase update proposal",
    "version": "16.0.1.0.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_update_proposal", "base_group_backend"],
    "data": ["security/ir.model.access.csv", "views/purchase_views.xml"],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["bealdav"],
}
