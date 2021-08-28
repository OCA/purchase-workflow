# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Procurement Batch Generator",
    "version": "14.0.1.0.0",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "summary": "Wizard to replenish from product tree view",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/procurement_batch_generator_view.xml",
    ],
    "installable": True,
}
