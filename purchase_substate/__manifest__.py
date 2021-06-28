# Copyright 2019 Akretion (<http://www.akretion.com>)
# Copyright 2020 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Sub State",
    "version": "13.0.1.0.0",
    "category": "Tools",
    "author": "Akretion,Ecosoft,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["base_substate", "purchase"],
    "data": [
        "views/purchase_views.xml",
        "data/purchase_substate_mail_template_data.xml",
        "data/purchase_substate_data.xml",
    ],
    "demo": ["data/purchase_substate_demo.xml"],
    "installable": True,
}
