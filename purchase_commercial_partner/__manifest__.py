# Copyright 2016-2022 Akretion France (https://akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Commercial Partner",
    "version": "16.0.1.0.0",
    "category": "Purchases",
    "license": "AGPL-3",
    "summary": "Add stored related field 'Commercial Supplier' on POs",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": ["views/purchase_order.xml", "views/purchase_report.xml"],
    "installable": True,
}
