# Copyright 2022 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Tags",
    "summary": "Allows to add multiple tags to purchase orders",
    "version": "16.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchases",
    "depends": ["purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_view.xml",
        "views/purchase_tag_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
