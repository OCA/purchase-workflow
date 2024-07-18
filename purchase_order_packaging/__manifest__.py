# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Order Packaging",
    "summary": """
        Allows to respect the packaging that is on sales orders when a
        purchase is automatically created from MTS+MTO rules""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "maintainers": ["mathieudelva"],
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase_stock",
        "stock_mts_mto_rule",
        "sale_management",
        "product_manufacturer",
        "sale_partner_incoterm",
    ],
}
