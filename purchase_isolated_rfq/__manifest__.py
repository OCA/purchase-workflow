# Copyright 2020 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Purchase Isolated RFQ",
    "version": "14.0.1.0.1",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "license": "AGPL-3",
    "data": ["data/ir_sequence_data.xml", "views/purchase_views.xml"],
    "maintainers": ["kittiu"],
    "installable": True,
    "uninstall_hook": "uninstall_hook",
    "post_init_hook": "post_init_hook",
}
