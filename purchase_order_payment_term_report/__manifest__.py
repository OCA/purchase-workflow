# Copyright 2022 Ooops - Ashish Hirpara <ashish.hirapara1995@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Report Payment Term",
    "version": "14.0.1.0.0",
    "author": "ooops404, Ashish Hirapara, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "summary": """Display Purchase Payment Terms in PO Report""",
    "data": [
        "reports/report_purchase_order.xml",
        "views/purchase_order.xml",
    ],
    "depends": ["purchase"],
    "installable": True,
}
