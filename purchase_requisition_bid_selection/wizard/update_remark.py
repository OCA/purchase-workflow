# -*- coding: utf-8 -*-
#    Copyright 2015 Camptocamp SA
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
from openerp import models, api, fields


class UpdateRemark(models.TransientModel):
    _name = "update.remark"

    def get_default_remark(self):
        ctx = self.env.context
        return self.env[ctx['active_model']].browse(ctx['active_id']).remark

    remark = fields.Text(default=get_default_remark)

    @api.multi
    def update_remark(self):
        self.ensure_one()
        ctx = self.env.context
        pol = self.env[ctx['active_model']].browse(ctx['active_id'])
        pol.remark = self.remark
        return {'type': 'ir.actions.act_window_close'}
