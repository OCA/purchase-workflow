# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import orm, fields


class purchase_internal_validation_installer(orm.TransientModel):
    _name = 'purchase.internal.validation.installer'
    _inherit = 'res.config'
    _columns = {
        'limit_amount': fields.integer(
            'Maximum Purchase Amount', required=True,
            help="Maximum amount after which internal validation of"
                 " purchase is required.",
        ),
    }

    _defaults = {
        'limit_amount': 5000,
    }

    def execute(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)
        if not data:
            return {}
        amt = data[0]['limit_amount']
        data_pool = self.pool['ir.model.data']
        transition_obj = self.pool['workflow.transition']
        cond_over = 'amount_total >= {0}'.format(amt)
        cond_under = 'amount_total < {0}'.format(amt)
        for module, extid, condition in [
                ("purchase_internal_validation",
                 "trans_draft_waiting_internal_validation",
                 cond_over),
                ("purchase",
                 "trans_draft_confirmed",
                 cond_under),
                ("purchase_internal_validation",
                 "trans_sent_waiting_internal_validation",
                 cond_over),
                ("purchase",
                 "trans_sent_confirmed",
                 cond_under)]:
            transition = data_pool.get_object(cr, uid, module, extid,
                                              context=context)
            transition.write({"condition": condition})
        return {}
