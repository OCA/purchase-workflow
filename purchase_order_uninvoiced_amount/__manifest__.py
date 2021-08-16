# Copyright 2020 Tecnativa - Manuel Calero
# Copyright 2020 Tecnativa - João Marques
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Purchase Order Univoiced Amount",
    "summary": "Show uninvoiced amount on purchase order tree.",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "version": "14.0.1.1.0",
    "development_status": "Beta",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase"],
    "data": ["views/purchase_order_view.xml"],
}
