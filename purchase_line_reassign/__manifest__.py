# Copyright 2018 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Purchase Line Reassign",
    "summary": "",
    "version": "15.0.1.0.0",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/purchase_line_reassign_view.xml",
    ],
}
