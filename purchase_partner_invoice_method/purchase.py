# -*- encoding: utf-8 -*-
##############################################################################
#
#    Purchase Partner Invoice Method for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp.osv import orm


class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = super(PurchaseOrder, self).onchange_partner_id(
            cr, uid, ids, partner_id, context=context)
        if partner_id:
            partner = self.pool['res.partner'].browse(
                cr, uid, partner_id, context=context)
            if partner.supplier_invoice_method:
                res['value']['invoice_method'] = \
                    partner.supplier_invoice_method
        return res
