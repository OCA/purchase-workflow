# -*- coding: utf-8 -*-
from . import model

from odoo import SUPERUSER_ID
from odoo.api import Environment


def workaround_create_initial_rules(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    WH = env['stock.warehouse']
    whs = WH.search([('buy_vci_to_resupply', '=', True)])
    whs.write({'buy_vci_to_resupply': True})
