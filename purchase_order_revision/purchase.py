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

from openerp.osv import fields, orm

class purchase_order(orm.Model):

    _inherit = "purchase.order"
    
    _columns = {
        'current_revision_id': fields.many2one('purchase.order','Current revision', readonly=True),
        'old_revision_ids': fields.one2many('purchase.order','current_revision_id',
            'Old revisions', readonly=True),
        }
    
    def new_revision(self, cr, uid, ids, context=None):
        if len(ids) > 1:
            raise orm.except_orm(_('Error'), _('This only works for 1 PO at a time'))
        po = self.browse(cr, uid, ids[0], context)
        new_seq = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order') or '/'
        old_seq = po.name
        po.write({'name': new_seq}, context=context)
        new_id = self.copy(cr, uid, po.id, default={'name': old_seq}, context=None)
        self.write(cr, uid, [new_id], {'current_revision_id': po.id}, context=context)
        self.action_cancel_draft(cr, uid, [po.id], context=context)
        return True
