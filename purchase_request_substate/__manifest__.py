# Copyright 2021 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Request Sub State",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["base_substate", "purchase_request"],
    "data": [
        "views/purchase_request_views.xml",
        "data/purchase_substate_mail_template_data.xml",
        "data/purchase_request_substate_data.xml",
    ],
    "demo": ["demo/purchase_request_substate_demo.xml"],
    "installable": True,
}
