# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2013-2014 Camptocamp SA
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
from openerp import models, fields, api


class action_modal(models.TransientModel):
    _name = 'purchase.action_modal'

    @api.multi
    def action(self):
        for e in ('active_model', 'active_ids', 'action'):
            if e not in self._context:
                return False
        ctx = {'active_ids': self._ids,
               'active_id': self._ids[0]}
        model = self.env[self._context['active_model']]
        rec = model.browse(self._context['active_ids'])
        res = getattr(rec.with_context(ctx),
                      self._context['action'])()
        if isinstance(res, dict):
            return res
        return {'type': 'ir.actions.act_window_close'}


class action_modal_datetime(models.TransientModel):
    _name = 'purchase.action_modal.datetime'
    _inherit = 'purchase.action_modal'

    datetime = fields.Datetime('Date')
