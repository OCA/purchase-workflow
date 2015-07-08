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


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    current_revision_id = fields.Many2one('purchase.order',
                                          'Current revision',
                                          copy=True,
                                          readonly=True)
    old_revision_ids = fields.One2many('purchase.order',
                                       'current_revision_id',
                                       'Old revisions',
                                       readonly=True,
                                       context={'active_test': False})
    revision_number = fields.Integer('Revision',
                                     copy=False)
    unrevisioned_name = fields.Char('Order Reference',
                                    copy=False,
                                    readonly=True)
    active = fields.Boolean('Active',
                            default=True,
                            copy=True)

    _sql_constraints = [
        ('revision_unique',
         'unique(unrevisioned_name, revision_number, company_id)',
         'Order Reference and revision must be unique per Company.'),
    ]

    @api.multi
    def new_revision(self):
        self.ensure_one()
        old_name = self.name
        revno = self.revision_number
        self.write({'name': '%s-%02d' % (self.unrevisioned_name,
                                         revno + 1),
                    'revision_number': revno + 1})
        # 'orm.Model.copy' is called instead of 'self.copy' in order to avoid
        # 'purchase.order' method to overwrite our values, like name and state
        defaults = {'name': old_name,
                    'revision_number': revno,
                    'active': False,
                    'state': 'cancel',
                    'current_revision_id': self.id,
                    'unrevisioned_name': self.unrevisioned_name,
                    }
        old_revision = super(PurchaseOrder, self).copy(default=defaults)
        self.action_cancel_draft()
        msg = _('New revision created: %s') % self.name
        self.message_post(body=msg)
        old_revision.message_post(body=msg)
        return True

    @api.model
    def create(self, values):
        if 'unrevisioned_name' not in values:
            if values.get('name', '/') == '/':
                seq = self.env['ir.sequence']
                values['name'] = seq.next_by_code('purchase.order') or '/'
            values['unrevisioned_name'] = values['name']
        return super(PurchaseOrder, self).create(values)
