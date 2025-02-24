# Copyright (C) 2021-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase - Add Products from BoM",
    "version": "16.0.1.0.0",
    "author": "Akretion," "Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "depends": [
        "purchase_mrp",
    ],
    "website": "https://github.com/OCA/purchase-workflow",
    "development_status": "Mature",
    "maintainers": [
        "mbcosta",
    ],
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Wizard
        "wizard/add_products_from_bom_view.xml",
        # Views
        "views/purchase_order_view.xml",
    ],
    "installable": True,
}
