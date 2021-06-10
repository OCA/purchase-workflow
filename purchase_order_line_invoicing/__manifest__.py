# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Order Line Invoicing",
    "summary": """
        Allows to invoice lines of multiple purchase orders""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": [
        "security/purchase_order_line_invoice_wizard.xml",
        "security/purchase_order_line_invoice_details.xml",
        "views/res_partner_views.xml",
        "wizards/purchase_order_line_invoicing_wizard.xml",
    ],
}
