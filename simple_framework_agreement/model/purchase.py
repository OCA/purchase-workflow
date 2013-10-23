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


class purchase_order(orm.Model):
    """Add on chnage on price to raise a warning if line is subject to
    an agreement"""

    _inherit = "purchase.order.line"

    def onchange_price(self, cr, uid, ids, price, date, supplier_id, product_id, context=None):
        """Raise a warning if a agreed price is changed"""
        if context is None:
            context = {}
        if not supplier_id or not ids:
            return {}
        agreement_obj = self.pool['framework.agreement']
        agreement = agreement_obj.get_product_agreement_price(cr, uid, product_id,
                                                       supplier_id, date,
                                                       context=context)
        if ag_price is not None and agreement.price != price:
            msg = _("You have set the price to %s \n"
                    " but there is a running agreement"
                    " with price %s") % (agreement.price, ag_price)
            return {'warning': {'title': _('Agreement Warning!'),
                                'message': msg}}
        return {}
