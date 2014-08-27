# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields, osv


class action_modal(osv.TransientModel):
    _name = "purchase.action_modal"
    _columns = {}

    def action(self, cr, uid, ids, context):
        for e in ('active_model', 'active_ids', 'action'):
            if e not in context:
                return False
        ctx = context.copy()
        ctx['active_ids'] = ids
        ctx['active_id'] = ids[0]
        res = getattr(self.pool.get(context['active_model']), context['action'])(cr, uid, context['active_ids'], context=ctx)
        if isinstance(res, dict):
            return res
        return {'type': 'ir.actions.act_window_close'}


class action_modal_datetime(osv.TransientModel):
    _name = "purchase.action_modal_datetime"
    _inherit = "purchase.action_modal"
    _columns = {
        'datetime': fields.datetime('Date'),
    }
