# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Request Packaging",
    "summary": """
        Allows to use product packaging on a purchase request""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase_request",
    ],
    "data": [
        "views/purchase_request.xml",
        "views/purchase_request_line.xml",
    ],
    "demo": [],
}
