# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Manual add supplierinfo group",
    "summary": "Glue module for compatibility between purchase manual "
    "add supplierinfo and group",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": " Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "purchase_manual_add_supplierinfo",
        "product_supplierinfo_group",
    ],
    "data": [],
    "demo": [],
    "auto-install": True,
}
