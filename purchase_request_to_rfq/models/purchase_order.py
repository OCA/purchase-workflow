# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
from openerp.osv import fields, orm
from openerp.tools.translate import _

class PurchaseOrder(orm.Model):
    _inherit = "purchase.order"

    def _key_fields_for_grouping_lines(self):
        """Return a list of fields used to identify order lines that can be
        merged.

        Lines that have this fields equal can be merged.

        This function can be extended by other modules to modify the list.
        """
        res = super(PurchaseOrder, self)._key_fields_for_grouping_lines()
        res = list(res)
        res.append('purchase_request_lines')
        return tuple(res)

    def _purchase_request_confirm_message_content(self, cr, uid, po,
                                                  request, request_dict,
                                                  context=None):
        if not request_dict:
            request_dict = {}
        title = _('Order confirmation %s for your Request %s') % (
            po.name, request.name)
        message = '<h3>%s</h3><ul>' % title
        message += _('The following requested items from Purchase Request %s '
                     'have now been confirmed in Purchase Order %s:') % (
            request.name, po.name)

        for line in request_dict.values():
            message += _(
                '<li><b>%s</b>: Ordered quantity %s %s, Planned date %s</li>'
            ) % (line['name'],
                 line['product_qty'],
                 line['product_uom'],
                 line['date_planned'],
                 )
        message += '</ul>'
        return message

    def _purchase_request_confirm_message(self, cr, uid, ids, context=None):
        request_obj = self.pool['purchase.request']
        for po in self.browse(cr, uid, ids, context=context):
            requests_dict = {}
            for line in po.order_line:
                for request_line in line.purchase_request_lines:
                    request_id = request_line.request_id.id
                    if request_id not in requests_dict:
                        requests_dict[request_id] = {}
                    date_planned = "%s" % line.date_planned
                    data = {
                        'name': request_line.name,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.name,
                        'date_planned': date_planned,
                    }
                    requests_dict[request_id][request_line.id] = data
            for request_id in requests_dict.keys():
                request = request_obj.browse(cr, uid, request_id,
                                             context=context)
                message = self._purchase_request_confirm_message_content(
                    cr, uid, po, request, requests_dict[request_id],
                    context=context)
                request_obj.message_post(cr, uid, [request_id],
                                         body=message)
        return True

    def _purchase_request_line_check(self, cr, uid, ids, context=None):
        for po in self.browse(cr, uid, ids, context=context):
            for line in po.order_line:
                if line.purchase_state == 'done':
                    raise orm.except_orm(
                        _('Warning !'),
                        _('Purchase Request %s has already been completed'))
        return True

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        self._purchase_request_line_check(
                cr, uid, ids, context=context)
        res = super(PurchaseOrder, self).wkf_confirm_order(cr, uid, ids,
                                                           context=context)
        self._purchase_request_confirm_message(
                cr, uid, ids, context=context)
        return res


class PurchaseOrderLine(orm.Model):
    _inherit = "purchase.order.line"

    def _has_purchase_request_lines(self, cr, uid, ids, field_names, arg,
                                    context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.purchase_request_lines:
                res[line.id] = True
            else:
                res[line.id] = False
        return res

    _columns = {
        'purchase_request_lines': fields.many2many(
            'purchase.request.line',
            'purchase_request_purchase_order_line_rel',
            'purchase_order_line_id',
            'purchase_request_line_id',
            'Purchase Request Lines', readonly=True),
        'has_purchase_request_lines': fields.function(
            _has_purchase_request_lines, type='boolean',
            string="Has Purchase Request Lines")
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'purchase_request_lines': [],
        })
        return super(PurchaseOrderLine, self).copy(
            cr, uid, id, default, context)

    def action_openRequestLineTreeView(self, cr, uid, ids, context=None):
        """
        :return dict: dictionary value for created view
        """
        if context is None:
            context = {}
        order_line = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(
            cr, uid, 'purchase_request',
            'purchase_request_line_form_action', context)
        request_line_ids = [request_line.id for request_line
                            in order_line.purchase_request_lines]
        res['domain'] = "[('id', 'in', ["+','.join(
            map(str, request_line_ids))+"])]"
        res['nodestroy'] = False
        return res
