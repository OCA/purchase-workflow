# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Update Date Planned At Confirm",
    "summary": """This module allows to update the planned date from products "
    "configuration at order confirmation""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "base_partition",
        "purchase",
    ],
    "data": ["views/res_config_settings.xml"],
}
