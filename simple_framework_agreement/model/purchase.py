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
from openerp.osv import orm
from openerp.tools.translate import _


class purchase_order_line(orm.Model):
    """Add on change on price to raise a warning if line is subject to
    an agreement"""

    _inherit = "purchase.order.line"

    def onchange_price(self, cr, uid, ids, price, date, supplier_id, product_id, context=None):
        """Raise a warning if a agreed price is changed"""
        if context is None:
            context = {}
        if not supplier_id or not ids:
            return {}
        agreement_obj = self.pool['framework.agreement']
        agreement = agreement_obj.get_product_agreement(cr, uid, product_id,
                                                        supplier_id, date,
                                                        context=context)
        if agreement is not None and agreement.price != price:
            msg = _("You have set the price to %s \n"
                    " but there is a running agreement"
                    " with price %s") % (price, agreement.price)
            return {'warning': {'title': _('Agreement Warning!'),
                                'message': msg}}
        return {}

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                            partner_id, date_order=False, fiscal_position_id=False,
                            date_planned=False, name=False, price_unit=False,
                            state='draft', context=None):
        # rock n'roll
        res = super(purchase_order_line, self).onchange_product_id(
                cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id,
                date_planned=date_planned,
                name=name, price_unit=price_unit, state=state, context=context
        )
        if qty:
            warning = self.onchange_quantity(cr, uid, ids, qty, date_order, partner_id,
                                             product_id, context)
            res.update(warning)
        return res

    def onchange_quantity(self, cr, uid, ids, qty, date, supplier_id, product_id, context=None):
        """Raise a warning if agreed qty is not sufficient"""
        if context is None:
            context = {}
        if not supplier_id or not ids:
            return {}
        agreement_obj = self.pool['framework.agreement']
        agreement = agreement_obj.get_product_agreement(cr, uid, product_id,
                                                        supplier_id, date,
                                                        context=context)
        if agreement is not None and agreement.available_quantity < qty:
            msg = _("You have ask for a quantity of %s \n"
                    " but there is only %s available"
                    " for current agreement") % (qty, agreement.available_quantity)
            return {'warning': {'title': _('Agreement Warning!'),
                                'message': msg}}
        return {}
