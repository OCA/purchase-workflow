# Copyright 2016 ForgeFlow S.L. (<http://www.forgeflow.com>)
# Copyright 2018 Hizbul Bahar <hizbul25@gmail.com>
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Location by Line",
    "summary": "Allows to define a specific destination location on each PO line",
    "version": "13.0.2.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": ["purchase_stock", "purchase_delivery_split_date"],
    "license": "AGPL-3",
    "data": ["views/purchase_view.xml"],
    "installable": True,
}
