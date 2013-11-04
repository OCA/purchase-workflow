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
from openerp.osv import orm
from .adapter_util import BrowseAdapterSourceMixin
from .logistic_requisition_source import AGR_PROC


class logistic_requisition_line(orm.Model, BrowseAdapterSourceMixin):
    """Override to enabale to generation of source line"""

    _inherit = "logistic.requisition.line"

    def _map_agr_requisiton_to_source(self, cr, uid, line, context=None,
                                      qty=0, agreement=None, **kwargs):
        """Prepare data dict for source line using agreement as source

        :params line: browse record of origin requistion.line
        :params agreement: browse record of origin agreement
        :params qty: quantity to be set on source line
        :returns: dict to be used by Model.create

        """
        res = {}
        direct_map = {
            'proposed_product_id': 'product_id',
            'requisition_line_id': 'id',
            'proposed_uom_id': 'requested_uom_id'}

        if not agreement:
            raise ValueError("Missing agreement")
        if not agreement.product_id.id == line.product_id.id:
            raise ValueError("Product mismatch for agreement and requisition line")
        res['unit_cost'] = agreement.get_price(qty)
        res['proposed_qty'] = qty
        res['agreement_id'] = agreement.id
        res['procurement_method'] = AGR_PROC
        res.update(self._direct_map(line, direct_map))
        return res

    def _map_requisition_to_source(self, cr, uid, line, context=None,
                                   qty=0, **kwargs):
        """Prepare data dict to generate source line using requisition as source

        :params line: browse record of origin requistion.line
        :params qty: quantity to be set on source line
        :returns: dict to be used by Model.create

        """
        res = {}
        direct_map = {'proposed_product_id': 'product_id',
                      'requisition_line_id': 'id',
                      'proposed_uom_id': 'requested_uom_id'}
        res['unit_cost'] = 0.0
        res['proposed_qty'] = qty
        res['agreement_id'] = False
        res['procurement_method'] = 'procurement'
        res.update(self._direct_map(line, direct_map))
        return res

    def _generate_lines_from_agreements(self, cr, uid, container, line,
                                        agreements, qty, context=None):
        """Generate 1/n source line(s) for one requisition line.

        This is done using available agreements.
        We first look for cheapeast agreement.
        Then if no more quantity are available and there is still remaining needs
        we look for next cheapest agreement or return remianing qty

        :param container: iterator of agreements browse
        :param qty: quantity to be sourced
        :param line: origin requisition line
        :returns: remaining quantity to source

        """
        if not agreements:
            return qty
        agreements.sort(key=lambda x: x.get_price(qty))
        current_agr = agreements.pop(0)
        avail = current_agr.available_quantity
        if not avail:
            return qty
        avail_sold = avail - qty
        to_consume = qty if avail_sold >= 0 else avail

        source_id = self.make_source_line(cr, uid, line, force_qty=to_consume,
                                          agreement=current_agr, context=context)
        container.append(source_id)
        difference = qty - to_consume
        if difference:
            return self._generate_lines_from_agreements(cr, uid, container, line,
                                                        agreements, difference, context=context)
        else:
            return 0

    def _source_lines_for_agreements(self, cr, uid, line, agreements):
        """Generate 1/n source line(s) for one requisition line

        This is done using available agreements.
        We first look for cheapeast agreement.
        Then if no more quantity are available and there is still remaining needs
        we look for next cheapest agreement or we create a tender source line

        :param line: requisition line browse record
        :returns: (generated line ids, remaining qty not covered by agreement)

        """
        qty = line.requested_qty
        generated = []
        remaining_qty = self._generate_lines_from_agreements(cr, uid, generated,
                                                             line, agreements, qty)
        return (generated, remaining_qty)

    def make_source_line(self, cr, uid, line, force_qty=None, agreement=None, context=None):
        """Generate a source line for a tender from a requisition line

        :param line: browse record of origin logistic.request
        :param force_qty: if set this quantity will be used instead
        of requested quantity
        :returns: id of generated source line

        """
        qty = force_qty if force_qty else line.requested_qty
        src_obj = self.pool['logistic.requisition.source']
        if agreement:
            return src_obj._make_source_line_from_origin(cr, uid, line,
                                                         self._map_agr_requisiton_to_source,
                                                         context=context, qty=qty,
                                                         agreement=agreement)
        else:
            return src_obj._make_source_line_from_origin(cr, uid, line,
                                                         self._map_requisition_to_source,
                                                         context=context, qty=qty)

    def _generate_source_line(self, cr, uid, line, context=None):
        """Generate one or n source line(s) per requisition line.

        Depending on the available resources. If there is framework agreement(s)
        running we generate one or n source line using agreements otherwise we generate one
        source line using tender process

        :param line: browse record of origin logistic.request
        :returns: list of generated source line ids

        """
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
                generated_lines.append(self.make_source_line(cr, uid, line,
                                                             force_qty=missing_qty))
        else:
            generated_lines.append(self.make_source_line(cr, uid, line))

        return generated_lines

    def _do_confirm(self, cr, uid, ids, context=None):
        """Override to generate source lines from requision line.

        Please refer to _generate_source_line documentation

        """
        res = super(logistic_requisition_line, self)._do_confirm(cr, uid, ids,
                                                                 context=context)
        for line_br in self.browse(cr, uid, ids, context=context):
            self._generate_source_line(cr, uid, line_br, context=context)
        return res
