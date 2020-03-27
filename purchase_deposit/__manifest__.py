# Copyright 2019 Elico Corp, Dominique K. <dominique.k@elico-corp.com.sg>
# Copyright 2019 Ecosoft Co., Ltd., Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Deposit",
    "version": "13.0.1.0.0",
    "summary": "Option to create deposit from purchase order",
    "author": "Elico Corp, Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "data": [
        "wizard/purchase_make_invoice_advance_views.xml",
        "views/res_config_settings_views.xml",
        "views/purchase_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
