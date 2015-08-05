# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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


from openerp import api, fields, models


class ProcurementBatchGenerator(models.TransientModel):
    _inherit = 'procurement.batch.generator'

    @api.model
    def _is_product_to_add(self, order_line):
        """ You can add rules to determine if the product of the order line
        should be in the default line
        """
        return True

    @api.model
    def _get_order_line(self, sale_order):
        """ Take order line with product to initialize procurement line
        """
        res = []
        for line in sale_order.order_line:
            if line.product_id:
                if self._is_product_to_add(line):
                    res.append(line)
        return res

    @api.model
    def _prepare_batch_generator_line(self, order_line, warehouse_id, today):
        return {
            'product_id': order_line.product_id.id,
            'partner_id': order_line.product_id.seller_id.id or False,
            'qty_available': order_line.product_id.qty_available,
            'outgoing_qty': order_line.product_id.outgoing_qty,
            'incoming_qty': order_line.product_id.incoming_qty,
            'uom_id': order_line.product_uom.id,
            'procurement_qty': order_line.product_uom_qty,
            'warehouse_id': warehouse_id,
            'date_planned': today,
        }

    @api.model
    def _default_lines(self):
        """ If active model is sale order
            create procurement for product in sale order line
        """
        if self.env.context['active_model'] != 'sale.order':
            return super(ProcurementBatchGenerator, self)._default_lines()

        res = []
        sale_obj = self.env['sale.order']
        sale_order = sale_obj.browse(self.env.context['active_id'])
        warehouse_id = sale_order.warehouse_id.id
        today = fields.Date.context_today(self)
        for line in self._get_order_line(sale_order):
            res.append(self._prepare_batch_generator_line(line, warehouse_id,
                                                          today))
        return res

    line_ids = fields.One2many(default=_default_lines)

    @api.multi
    def validate(self):
        """ When validate the wizard, validate sale order if valid_so is in
        the context
        """
        res = super(ProcurementBatchGenerator, self).validate()
        if self.env.context.get('valid_so'):
            # confirm the sale order
            sale_obj = self.env['sale.order']
            sale_order = sale_obj.browse(self.env.context['active_id'])
            sale_order.action_button_confirm()
        return res
