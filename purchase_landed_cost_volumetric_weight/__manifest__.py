# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

{
    "name": "Purchase landed costs volumetric weight",
    "version": "13.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_landed_cost", "delivery_price_rule_volumetric_weight"],
    "data": ["views/purchase_cost_distribution_view.xml"],
    "installable": True,
    "maintainers": ["victoralmau"],
}
