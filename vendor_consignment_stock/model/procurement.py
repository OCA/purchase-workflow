# -*- coding: utf-8 -*-
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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
from openerp import models, api


class Procurement(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _run(self, procurement):
        if procurement.rule_id and procurement.rule_id.action == 'buy_vci':
            return procurement.make_vci_po()
        return super(Procurement, self)._run(procurement)

    @api.multi
    def make_vci_po(self):
        """Returns a dict {procurement_id: generated_purchase_line_id}."""
        line_model = self.env['purchase.order.line']

        result = self.make_po()
        for proc in self:
            # The order line id can be False if there was an error.
            # Do nothing in that case because errors are handled in make_po().
            if result.get(proc.id):
                order_line = line_model.browse(result[proc.id])

                order_line.order_id.is_vci = True

                # As no picking is generated for this kind
                # of purchase, it must be generated on order
                if order_line.order_id.invoice_method == 'picking':
                    order_line.order_id.invoice_method = 'order'

        return result

    @api.model
    def _get_product_supplier(self, procurement):
        """In the VCI case, choose the owner in the sale line as supplier."""
        if procurement.rule_id.action == 'buy_vci':
            return procurement.move_dest_id.restrict_partner_id
        else:
            return super(Procurement, self)._get_product_supplier(procurement)

    @api.model
    def _check(self, procurement):
        if procurement.rule_id and procurement.rule_id.action == 'buy_vci':
            purchase = procurement.purchase_id
            if purchase and purchase.state in ['approved', 'done']:
                procurement.move_dest_id.state = 'confirmed'
                procurement.move_dest_id.action_assign()
                return True
            else:
                return False
        else:
            return super(Procurement, self)._check(procurement)
