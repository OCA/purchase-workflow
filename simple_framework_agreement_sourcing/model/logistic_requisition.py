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
from openerp.addons.simple_framework_agreement.utils import id_boilerplate
from openerp.addons.simple_framework_agreement.model.framework_agreement import\
    FrameworkAgreementObservable


class logistic_requisition_source(orm.Model, FrameworkAgreementObservable):
    """Add support of simple framework agreement"""

    _inherit = "logistic.requisition.source"

    _columns = {'agreement_id': fields.many2one('framework.agreement',
                                                'Agreement'),
                'agreement_id_dummy': fields.many2one('framework.agreement',
                                                      'Agreement'),
                'supplier_id': fields.related('agreement_id', 'supplier_id',
                                              type='many2one',  relation='res.partner',
                                              string='Agreement Supplier')}

    def _get_date(self, cr, uid, source_id, context=None):
        current = self.browse(cr, uid, source_id, context=context)
        now = fields.datetime.now()
        return current.requisition_id.date or now

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
