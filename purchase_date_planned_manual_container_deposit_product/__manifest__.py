# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Date Planned Manual Container Deposit Product",
    "summary": """Glue module between purchase_date_planned_manual
     and purchase_product_packaging_container_deposit""",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": [
        "purchase_date_planned_manual",
        "purchase_product_packaging_container_deposit",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "auto_install": True,
}
