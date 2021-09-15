# Copyright 2016 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Minimum Amount",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "14.0.1.0.1",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_order_approval_block"],
    "data": [
        "data/purchase_block_reason_data.xml",
        "views/purchase_order_view.xml",
        "views/res_partner_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
