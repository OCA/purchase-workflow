# Copyright 2020 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Invoice New Picking Line",
    "summary": """When creating an invoice from a purchase order, this module
        also adds invoice lines for products that were in the order's pickings
        but not in the order itself.""",
    "version": "16.0.1.0.0",
    "author": "Coop IT Easy SCRLfs, Odoo Community Association (OCA)",
    "category": "Purchase",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_stock"],
    "installable": True,
}
