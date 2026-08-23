# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    create_warehouse_stock_rules(env)


def create_warehouse_stock_rules(env):
    warehouses = env["stock.warehouse"].with_context(active_test=False).search([])
    warehouses._set_subcontracting_service_proc_rule()
