# -*- coding: utf-8 -*-
from . import model
from . import wizard

from openerp import SUPERUSER_ID


def fix_inconsistent_initial_types(cr, registry):
    """A post init hook executed when the module is installed."""
    PO = registry['purchase.order']
    approved_ids = PO.search(cr, 1, [
        ('state', '=', 'approved')
    ])
    PO.write(cr, SUPERUSER_ID, approved_ids, {'type': 'purchase'})
