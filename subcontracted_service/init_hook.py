# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import SUPERUSER_ID
from openerp.api import Environment


def post_init_hook(cr, pool):
    env = Environment(cr, SUPERUSER_ID, {})
    create_warehouse_procurement_rules(env)


def create_warehouse_procurement_rules(env):
    warehouses = env['stock.warehouse'].with_context(
        active_test=False).search([])
    warehouses._set_subcontracting_service_proc_rule()
