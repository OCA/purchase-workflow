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
from .logistic_requisition_source import AGR_PROC


class logistic_requisition_cost_estimate(orm.Model):
    """Add update of agreement price"""

    _inherit = "logistic.requisition.cost.estimate"

    def _update_agreement_source(self, cr, uid, source, context=None):
        """Update price of source line using related confirmed PO"""
        if source.procurement_method == AGR_PROC:
            price = source.get_agreement_price_from_po()
            source.write({'unit_cost': price})
            source.refresh()

    def _prepare_cost_estimate_line(self, cr, uid, sourcing, context=None):
        """Override in order to update agreement source line

        We update the price of source line that will be used in cost estimate

        """
        self._update_agreement_source(cr, uid, sourcing, context=context)
        return super(logistic_requisition_cost_estimate,
                     self)._prepare_cost_estimate_line(cr, uid, sourcing,
                                                       context=context)
