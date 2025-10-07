# Copyright 2017-25 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Date Planned Manual",
    "summary": "This module makes the system to always respect the planned "
    "(or scheduled) date in PO lines.",
    "version": "16.0.1.0.1",
    "development_status": "Mature",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["LoisRForgeFlow"],
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": ["purchase_stock"],
    "data": [
        "views/purchase_order_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
