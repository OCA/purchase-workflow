# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
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
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.simple_framework_agreement.model.framework_agreement import\
    FrameworkAgreementObservable
from openerp.addons.simple_framework_agreement.utils import id_boilerplate

from .adapter_util import BrowseAdapterMixin, BrowseAdapterSourceMixin

AGR_PROC = 'fw_agreement'


class logistic_requisition_source(orm.Model, BrowseAdapterMixin,
                                  BrowseAdapterSourceMixin, FrameworkAgreementObservable):
    """Add support of simple framework agreement"""

    _inherit = "logistic.requisition.source"

    _columns = {'agreement_id': fields.many2one('framework.agreement',
                                                'Agreement'),
                # stupid trick to by pass onchange limitation on readonly
                'agreement_id_dummy': fields.related('agreement_id',
                                                     relation='framework.agreement',
                                                     type='many2one',
                                                     string='Agreement'),
                'supplier_id': fields.related('agreement_id', 'supplier_id',
                                              type='many2one',  relation='res.partner',
                                              string='Agreement Supplier')}

    #------------------ adapting source line to po -----------------------------

    def _map_source_to_po(self, cr, uid, line, context=None, **kwargs):
        """Map source line to dict to be used by PO create
        defaults are optional"""
        supplier = line.agreement_id.supplier_id
        add = line.requisition_id.consignee_shipping_id
        term = supplier.property_supplier_payment_term
        term = term.id if term else False
        position = supplier.property_account_position
        position = position.id if position else False

        data = {}
        data['partner_id'] = supplier.id
        data['company_id'] = self._company(cr, uid, context)
        data['pricelist_id'] = supplier.property_product_pricelist_purchase.id
        data['address_id'] = add.id
        data['location_id'] = add.property_stock_customer.id
        data['payment_term_id'] = term
        data['fiscal_position'] = position
        data['origin'] = line.requisition_id.name
        data['date_order'] = line.requisition_id.date
        data['name'] = line.requisition_id.name
        return data

    def _map_source_to_po_line(self, cr, uid, line, context=None, **kwargs):
        """Map source line to dict to be used by PO line create
        Map source line to dict to be used by PO create
        defaults are optional"""
        acc_pos_obj = self.pool['account.fiscal.position']
        supplier = line.agreement_id.supplier_id
        taxes_ids = line.proposed_product_id.supplier_taxes_id
        taxes = acc_pos_obj.map_tax(cr, uid, supplier.property_account_position,
                                    taxes_ids)
        data = {}
        direct_map = {'qty': 'proposed_qty',
                      'product_id': 'proposed_product_id',
                      'product_uom': 'proposed_uom_id',
                      'price_unit': 'unit_cost',
                      'lr_source_line_id': 'id'}

        data.update(self._direct_map(line, direct_map))
        data['name'] = line.proposed_product_id.id
        data['date_planned'] = line.requisition_id.date_delivery
        data['taxes_id'] = [(6, 0, taxes)]
        return data

    def _make_po_from_source_line(self, cr, uid, source_line, context=None):
        po_obj = self.pool['purchase.order']
        pid = po_obj._make_purchase_order_from_origin(cr, uid, source_line,
                                                      self._map_source_to_po,
                                                      self._map_source_to_po_line,
                                                      context=context)
        return pid

    def make_purchase_order(self, cr, uid, ids, context=None):
        po_ids = []
        for source_line in self.browse(cr, uid, ids, context=context):
            po_id = self._make_po_from_source_line(cr, uid, source_line, context=None)
            po_ids.append(po_id)
        return po_ids

    def action_create_agreement_po_requisition(self, cr, uid, ids, context=None):
        # We force empty context
        act_obj = self.pool.get('ir.actions.act_window')
        po_ids = self.make_purchase_order(cr, uid, ids, context=context)
        res = act_obj.for_xml_id(cr, uid,
                                 'purchase', 'purchase_rfq', context=context)
        res.update({'domain': [('id', 'in', po_ids)],
                    'res_id': False,
                    'context': '{}',
                    })
        return res

    def _is_sourced_fw_agreement(self, cr, uid, source, context=None):
        po_line_obj = self.pool['purchase.order.line']
        sources_ids = po_line_obj.search(cr, uid, [('lr_source_line_id', '=', source.id)],
                                         context=context)
        # predicate
        return bool(sources_ids)

    #---------------------- provide adapter middleware -------------------------

    def _make_source_line_from_origin(self, cr, uid, origin, map_fun,
                                      post_fun=None, context=None, **kwargs):
        model = self.pool['logistic.requisition.source']
        data = self._adapt_origin(cr, uid, model, origin, map_fun,
                                  post_fun=post_fun, context=context, **kwargs)
        self._validate_adapted_data(cr, uid, model, data, context=context)
        s_id = self.create(cr, uid, data, context=context)
        if callable(post_fun):
            post_fun(cr, uid, s_id, origin, context=context, **kwargs)
        return s_id

    #---------------OpenERP tedious onchange management ------------------------

    def _get_date(self, cr, uid, source_id, context=None):
        """helper to retrive date to be used by framework agreement
        when in source line context
        :param source_id: requisition.line.source id that should
        provide date
        :returns: date/datetime string"""
        current = self.browse(cr, uid, source_id, context=context)
        now = fields.datetime.now()
        return current.requisition_id.date or now

    @id_boilerplate
    def onchange_sourcing_method(self, cr, uid, source_id, method, proposed_product_id,
                                 proposed_qty=0, context=None):
        """
        Call when source method is set on a source line.
        If sourcing method is framework agreement
        it will set price, agreement and supplier if possible
        and raise quantity warning.
        """
        res = {'value': {'agreement_id': False,
                         'agreement_id_dummy': False}}
        if (method != AGR_PROC or not proposed_product_id or not source_id):
            return res
        agreement_obj = self.pool['framework.agreement']
        date = self._get_date(cr, uid, source_id, context=context)
        agreement, enough_qty = agreement_obj.get_cheapest_agreement_for_qty(cr, uid,
                                                                             proposed_product_id,
                                                                             date,
                                                                             proposed_qty,
                                                                             context=context)
        if not agreement:
            return res
        res['value'] = {'agreement_id': agreement.id,
                        'agreement_id_dummy': agreement.id,
                        'unit_cost': agreement.price,
                        'total_cost': agreement.price * proposed_qty,
                        'supplier_id': agreement.supplier_id.id}
        if not enough_qty:
            msg = _("You have ask for a quantity of %s \n"
                    " but there is only %s available"
                    " for current agreement") % (proposed_qty, agreement.available_quantity)
            res['warning'] = msg
        return res

    @id_boilerplate
    def onchange_price(self, cr, uid, source_id, method, price, supplier_id,
                       proposed_product_id, context=None):
        """Raise a warning if a agreed price is changed"""
        if (method != AGR_PROC or False in [proposed_product_id,
                                            supplier_id, source_id]):
            return {}
        date = self._get_date(cr, uid, source_id, context=context)
        return self.onchange_price_obs(cr, uid, source_id, price, date, supplier_id,
                                       proposed_product_id, context=None)

    @id_boilerplate
    def onchange_quantity(self, cr, uid, source_id, method, qty, supplier_id,
                          proposed_product_id, context=None):
        """Raise a warning if agreed qty is not sufficient"""
        if (method != AGR_PROC or not proposed_product_id or not source_id):
            return {}
        date = self._get_date(cr, uid, source_id, context=context)
        return self.onchange_quantity_obs(cr, uid, source_id, qty, date,
                                          supplier_id, proposed_product_id,
                                          context=context)

    @id_boilerplate
    def onchange_product_id(self, cr, uid, source_id, method,
                            proposed_product_id, proposed_qty, context=None):
        """Call when product is set on a source line.
        If sourcing method is framework agreement
        it will set price, agreement and supplier if possible
        and raise quantity warning."""
        if (method != AGR_PROC or not proposed_product_id or not source_id):
            return {}
        return self.onchange_sourcing_method(cr, uid, source_id, method, proposed_product_id,
                                             proposed_qty, context=context)
