# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock landed cost company percentage",
    "summary": "Fixed percentage of landed costs to every received items",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["stock_landed_costs"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_view.xml",
    ],
    "installable": True,
}
