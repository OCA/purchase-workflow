# -*- coding: utf-8 -*-
from . import model
from . import wizard


def fix_inconsistent_initial_types(cr, registry):
    PO = registry['purchase.order']
    approved_ids = registry['purchase.order'].search(cr, 1, [
        ('state', '=', 'approved')
    ])
    PO.write(cr, 1, approved_ids, {'type': 'purchase'})
