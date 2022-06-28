# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Purchase Lead Hour",
    "summary": "Allows to set more accurate vendor lead delays",
    "version": "14.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "maintainers": ["mmequignon"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "depends": ["purchase_stock"],
    "data": ["views/product_supplierinfo.xml"],
}
