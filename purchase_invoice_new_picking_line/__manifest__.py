# Copyright 2020 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Invoice New Picking Line",
    "summary": "When creating an invoice from incoming picking, also adds invoice lines for product that were not in the purchase order",
    "version": "12.0.1.0.0",
    "author": "Coop IT Easy SCRLfs, " "Odoo Community Association (OCA)",
    "category": "Purchase",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_stock"],
    "installable": True,
}
