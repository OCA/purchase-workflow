# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#    @author Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tools.translate import _


class purchase_order(models.Model):
    _inherit = "purchase.order"

    current_revision_id = fields.Many2one('purchase.order',
                                          'Current revision',
                                          readonly=True)
    old_revision_ids = fields.One2many('purchase.order',
                                       'current_revision_id',
                                       'Old revisions',
                                       readonly=True)

    @api.multi
    def new_revision(self):
        self.ensure_one()
        seq = self.env['ir.sequence']
        new_name = seq.next_by_code('purchase.order') or '/'
        old_name = self.name
        self.write({'name': new_name})
        # 'orm.Model.copy' is called instead of 'self.copy' in order to avoid
        # 'purchase.order' method to overwrite our values, like name and state
        defaults = {'name': old_name,
                    'state': 'cancel',
                    'shipped': False,
                    'invoiced': False,
                    'invoice_ids': [],
                    'picking_ids': [],
                    'old_revision_ids': [],
                    'current_revision_id': self.id,
                    }
        super(purchase_order, self).copy(default=defaults)
        self.action_cancel_draft()
        return True

    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        default.update({
            'old_revision_ids': [],
        })
        return super(purchase_order, self).copy(default)
