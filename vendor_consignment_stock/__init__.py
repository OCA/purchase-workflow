# -*- coding: utf-8 -*-
from . import model

from openerp import SUPERUSER_ID


def workaround_create_initial_rules(cr, registry):
    """Work around https://github.com/odoo/odoo/issues/4853."""
    WH = registry['stock.warehouse']
    wh_ids = WH.search(cr, SUPERUSER_ID, [('buy_vci_to_resupply', '=', True)])
    WH.write(cr, SUPERUSER_ID, wh_ids, {'buy_vci_to_resupply': True})
