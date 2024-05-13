# Copyright 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Cancel Reason",
    "version": "17.0.1.0.0",
    "author": "Camptocamp, Okia SPRL, Odoo Community Association (OCA)",
    "category": "Purchase",
    "license": "AGPL-3",
    "complexity": "normal",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_order_cancel.xml",
        "views/purchase_order.xml",
        "views/purchase_order_cancel_reason.xml",
        "data/purchase_order_cancel_reason.xml",
    ],
    "auto_install": False,
    "installable": True,
}
