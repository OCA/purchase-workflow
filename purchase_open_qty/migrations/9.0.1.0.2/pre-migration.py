# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services, S.L.
#   (<http://www.eficent.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.purchase_open_qty.init_hook import \
    store_field_qty_to_receive_and_invoice


def migrate(cr, version):
    if not version:
        return
    store_field_qty_to_receive_and_invoice(cr)
