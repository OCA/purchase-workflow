# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Uninvoiced Amount Force Invoiced Line",
    "version": "15.0.1.0.0",
    "category": "Purchases",
    "license": "AGPL-3",
    "summary": "Glue module between uninvoiced amount line and force invoiced line",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["JoanSForgeFlow"],
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase_order_uninvoiced_amount_line",
        "purchase_invoice_status_line",
    ],
    "data": [],
    "installable": True,
}
