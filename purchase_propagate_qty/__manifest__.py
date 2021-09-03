# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Propagate Quantity",
    "version": "12.0.1.0.0",
    "summary": "Quantity decrease on purchase line are propagated "
    "to the corresponding stock.move",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "depends": [
        "purchase_stock",
    ],
    "installable": True,
    "application": False,
}
