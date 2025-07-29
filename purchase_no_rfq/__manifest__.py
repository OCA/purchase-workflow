# Copyright (C) 2021-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Order - No Request For Quotation",
    "version": "17.0.1.1.0",
    "author": "GRAP,Odoo Community Association (OCA)",
    "maintainers": ["legalsylvain"],
    "license": "AGPL-3",
    "category": "Purchase Management",
    "depends": [
        "purchase",
    ],
    "website": "https://github.com/OCA/purchase-workflow",
    "data": [
        "reports/ir_actions_report.xml",
        "reports/purchase_order_template.xml",
        "views/view_purchase_order.xml",
    ],
    "uninstall_hook": "uninstall_hook",
    "installable": True,
}
