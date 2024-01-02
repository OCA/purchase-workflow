# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Invoice Create Security Group",
    "summary": """
        Allows to not display invoicing button on a purchase order if not in group""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": [
        "views/res_config_settings.xml",
        "security/security.xml",
        "views/purchase_order.xml",
    ],
}
