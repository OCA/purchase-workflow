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
from operator import attrgetter
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.simple_framework_agreement.utils import id_boilerplate
from openerp.addons.simple_framework_agreement.model.framework_agreement import\
    FrameworkAgreementObservable


class logistic_requisition_line(orm.Model):
    """Override to enabale to generation of source line"""

    _inherit = "logistic.requisition.line"

    def _get_data_using_agreement(self, cr, uid, line_br, agreement, qty, context=None):
        """Prepare data dict for source line using agreement as source"""
        res = {}
        if not agreement.product_id.id == line_br.product_id.id:
            raise ValueError("Product mismatch for agreement and requisition line")
        res['unit_cost'] = agreement.price
        res['proposed_qty'] = qty
        res['agreement_id'] = agreement.id
        res['proposed_product_id'] = line_br.product_id.id
        res['requisition_line_id'] = line_br.id
        res['procurement_method'] = 'fw_agreement'
        return res

    def _get_data_using_tender(self, cr, uid, line_br, qty, context=None):
        """Prepare data dict to generate source line using requisiton as source"""
        res = {}
        res['unit_cost'] = 0.0
        res['proposed_qty'] = qty
        res['agreement_id'] = False
        res['proposed_product_id'] = line_br.product_id.id
        res['requisition_line_id'] = line_br.id
        res['procurement_method'] = 'procurement'
        return res

    def _generate_lines_from_agreements(self, cr, uid, container, line,
                                        agreements, qty, context=None):
        """Generate source lines for one requisition line using
        available agreements. We first look for cheapeast agreement.
        Then if no more quantity are available and there is still remaining needs
        we look for next cheapest agreement or we create
        a tender source line
        :param container: iterator of agreements browser
        :param qty: quantity to be sourced
        :param line: origin requisition line
        :returns: remaining quantity to source
        """
        try:
            current_agr = agreements.next()
        except StopIteration:
            return qty
        src_obj = self.pool['logistic.requisition.source']
        avail = current_agr.available_quantity
        avail_sold = avail - qty
        to_consume = qty if avail_sold >= 0 else qty - avail_sold
        data = self._get_data_using_agreement(cr, uid, line, current_agr,
                                              to_consume, context)
        container.append(src_obj.create(cr, uid, data))
        difference = qty - to_consume
        if not difference:
            return 0
        return self._generate_lines_from_agreements(cr, uid, container, line,
                                                    agreements, difference)

    def _source_lines_for_agreements(self, cr, uid, line, agreements):
        """Generate source lines for one requisition line using
        available agreements. We first look for cheapeast agreement.
        Then if no more quantity are available and there is still remaining needs
        we look for next cheapest agreement or we create
        a tender source line
        """
        agreements.sort(key=attrgetter('price'))
        qty = line.requested_qty
        agr_iter = iter(agreements)
        generated = []
        remaining_qty = self._generate_lines_from_agreements(cr, uid, generated,
                                                             line, agr_iter, qty)
        return (generated, remaining_qty)

    def _source_line_for_tender(self, cr, uid, line, force_qty=None, context=None):
        """Generate a source line for a tender from a requisition line"""
        qty = force_qty if force_qty else line.requested_qty
        src_obj = self.pool['logistic.requisition.source']
        data = self._get_data_using_tender(cr, uid, line, qty, context)
        return src_obj.create(cr, uid, data, context=None)

    def _generate_source_line(self, cr, uid, line, context=None):
        """Generate one or n source line(s) per requisition line
        depending on the available resources. If there is framework agreement(s)
        running we generate one or n source line using agreements otherwise we generate one
        source line using tender process"""
        if line.source_ids:
            return None
        agr_obj = self.pool['framework.agreement']
        date = line.requisition_id.date
        product_id = line.product_id.id
        agreements = agr_obj.get_all_product_agreements(cr, uid, product_id, date,
                                                        context=context)
        generated_lines = []
        if agreements:
            line_ids, missing_qty = self._source_lines_for_agreements(cr, uid, line, agreements)
            generated_lines.extend(line_ids)
            if missing_qty:
                generated_lines.append(self._source_line_for_tender(cr, uid, line,
                                                                    force_qty=missing_qty))
        else:
            generated_lines.append(self._source_line_for_tender(cr, uid, line))

        return generated_lines

    def _do_confirm(self, cr, uid, ids, context=None):
        """Override to generate source lines from requision line.
        Please refer to _generate_source_line documentation"""
        res = super(logistic_requisition_line, self)._do_confirm(cr, uid, ids,
                                                                 context=context)
        for line_br in self.browse(cr, uid, ids, context=context):
            self._generate_source_line(cr, uid, line_br, context=context)
        return res


class logistic_requisition_source(orm.Model, FrameworkAgreementObservable):
    """Add support of simple framework agreement"""

    _inherit = "logistic.requisition.source"

    _columns = {'agreement_id': fields.many2one('framework.agreement',
                                                'Agreement'),
                # stupid trick to by pass onchnage limitation on readonly on change
                'agreement_id_dummy': fields.related('agreement_id',
                                                     relation='framework.agreement',
                                                     type='many2one',
                                                     string='Agreement'),
                'supplier_id': fields.related('agreement_id', 'supplier_id',
                                              type='many2one',  relation='res.partner',
                                              string='Agreement Supplier')}

    def _get_date(self, cr, uid, source_id, context=None):
        current = self.browse(cr, uid, source_id, context=context)
        now = fields.datetime.now()
        return current.requisition_id.date or now

    #---------------OpenERP tedious onchange management ------------------------------------------

    @id_boilerplate
    def onchange_sourcing_method(self, cr, uid, source_id, method, proposed_product_id,
                                 proposed_qty=0, context=None):
        """

        :param method:
        :param proposed_product_id:
        :param proposed_qty:
        """
        res = {'value': {'agreement_id': False,
                         'agreement_id_dummy': False}}
        if (method != 'fw_agreement' or not proposed_product_id or not source_id):
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
        if (method != 'fw_agreement' or False in [proposed_product_id,
                                                  supplier_id, source_id]):
            return {}
        date = self._get_date(cr, uid, source_id, context=context)
        return self.onchange_price_obs(cr, uid, source_id, price, date, supplier_id,
                                       proposed_product_id, context=None)

    @id_boilerplate
    def onchange_quantity(self, cr, uid, source_id, method, qty, supplier_id,
                          proposed_product_id, context=None):
        """Raise a warning if agreed qty is not sufficient"""
        if (method != 'fw_agreement' or not proposed_product_id or not source_id):
            return {}
        date = self._get_date(cr, uid, source_id, context=context)
        return self.onchange_quantity_obs(cr, uid, source_id, qty, date,
                                          supplier_id, proposed_product_id,
                                          context=context)

    @id_boilerplate
    def onchange_product_id(self, cr, uid, source_id, method,
                            proposed_product_id, proposed_qty, context=None):
        """Raise a warning if a agreed price is changed"""
        if (method != 'fw_agreement' or not proposed_product_id or not source_id):
            return {}
        return self.onchange_sourcing_method(cr, uid, source_id, method, proposed_product_id,
                                             proposed_qty, context=context)
