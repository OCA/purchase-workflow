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
        waiting = data_pool._get_id(cr, uid,
                                    'purchase_internal_validation',
                                    'trans_draft_waiting_internal_validation')
        waiting_id = data_pool.browse(cr, uid, waiting, context=context).res_id
        confirm = data_pool._get_id(cr, uid,
                                    'purchase', 'trans_draft_confirmed')
        confirm_id = data_pool.browse(cr, uid, confirm, context=context).res_id
        transition_obj.write(cr, uid, waiting_id,
                             {'condition': 'amount_total>=%s' % (amt)})
        transition_obj.write(cr, uid, confirm_id,
                             {'condition': 'amount_total<%s' % (amt)})
        return {}
