# -*- coding: utf-8 -*-
#    Copyright Camptocamp SA
#    @author: Guewen Baconnier
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from openerp import models, fields, api


class PurchaseExceptionConfirm(models.TransientModel):

    _name = 'purchase.exception.confirm'

    purchase_id = fields.Many2one('purchase.order', 'Purchase')
    exception_ids = fields.Many2many('purchase.exception',
                                     'purchase_exception_wiz_rel',
                                     string='Exceptions to resolve',
                                     readonly=True)
    ignore = fields.Boolean('Ignore Exceptions')

    @api.model
    def default_get(self, field_list):
        res = super(PurchaseExceptionConfirm, self).default_get(field_list)
        purchase_id = self._context.get('active_ids')
        assert len(purchase_id) == 1, ("Only 1 ID accepted, got %r" %
                                       purchase_id)
        purchase_id = purchase_id[0]
        purchase = self.env['purchase.order'].browse(purchase_id)
        exception_ids = [e.id for e in purchase.exception_ids]
        res.update({'exception_ids': [(6, 0, exception_ids)]})
        res.update({'purchase_id': purchase_id})
        return res

    @api.one
    def action_confirm(self):
        if self.ignore:
            self.purchase_id.ignore_exceptions = True
        return {'type': 'ir.actions.act_window_close'}
