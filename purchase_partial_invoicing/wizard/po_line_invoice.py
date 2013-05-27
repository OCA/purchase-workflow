# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
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
from openerp.tools.translate import _


class purchase_line_invoice(orm.TransientModel):

    _inherit = 'purchase.order.line_invoice'
    
    _columns = {
        'partial_invoice': fields.boolean('Partial invoicing'),
        'line_ids': fields.one2many('purchase.order.line_invoice.line','wizard_id','Lines'),
        }

class purchase_line_invoice_line(orm.TransientModel):

    _name = 'purchase.order.line_invoice.line'

    _columns = {
        'po_line_id': fields.many2one('purchase.order.line',
            'Purchase order line', readonly=True),
        'percentage': fields.float('Percentage'),
        'wizard_id': fields.many2one('purchase.order.line_invoice','Wizard'),
        }
