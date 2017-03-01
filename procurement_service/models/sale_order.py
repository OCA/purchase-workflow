# -*- coding: utf-8 -*-
# Copyright 2015 Avanzosc(http://www.avanzosc.es)
# Copyright 2015 Tecnativa (http://www.tecnativa.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    def action_button_confirm(self):
        procurement_obj = self.env['procurement.order']
        procurement_group_obj = self.env['procurement.group']
        res = super(SaleOrder, self).action_button_confirm()
        for line in self.order_line:
            valid = self._validate_service_product_for_procurement(
                line.product_id)
            if valid:
                if not self.procurement_group_id:
                    vals = self._prepare_procurement_group(self)
                    group = procurement_group_obj.create(vals)
                    self.write({'procurement_group_id': group.id})
                vals = self._prepare_order_line_procurement(
                    self, line, group_id=self.procurement_group_id.id)
                vals['name'] = self.name + ' - ' + line.product_id.name
                procurement_obj.create(vals)
        return res

    def _validate_service_product_for_procurement(self, product):
        routes = product.route_ids.filtered(
            lambda r: r.id in (self.env.ref('stock.route_warehouse0_mto').id,
                               self.env.ref('purchase.route_warehouse0_buy').id
                               ))
        return product.type == 'service' and len(routes) == 2
