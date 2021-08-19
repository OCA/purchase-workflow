# Copyright 2021 ProThai Technology Co.,Ltd. (http://prothaitechnology.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Request Type",
    "version": "14.0.1.0.1",
    "author": "ProThai, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Purchase Management",
    "depends": ["purchase_request"],
    "website": "https://github.com/OCA/purchase-workflow",
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/purchase_request_type_view.xml",
        "views/purchase_request_view.xml",
        "data/purchase_request_type.xml",
    ],
    "maintainer": ["prapassornS"],
    "installable": True,
    "auto_install": False,
}
