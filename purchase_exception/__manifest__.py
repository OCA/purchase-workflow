# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Exception",
    "summary": "Custom exceptions on purchase order",
    "version": "12.0.1.1.0",
    "category": "Generic Modules/Purchase",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase", "base_exception",],
    "license": "AGPL-3",
    "data": [
        "data/purchase_exception_data.xml",
        "wizard/purchase_exception_confirm_view.xml",
        "views/purchase_view.xml",
    ],
    "installable": True,
}
