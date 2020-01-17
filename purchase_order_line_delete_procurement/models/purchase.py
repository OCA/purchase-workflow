# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_cancel(self):
        purchase_context = dict(self._context, cancel_sale_order=True)
        res = super(PurchaseOrder, self.with_context(purchase_context)).button_cancel()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def unlink(self):
        if 'cancel_sale_order' not in self.env.context:
            for line in self:
                line.procurement_ids.filtered(lambda r: r.state != 'cancel').unlink()
        return super(PurchaseOrderLine, self).unlink()


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.multi
    def unlink(self):
        for procurement in self:
            if procurement.move_dest_id and \
                    procurement.move_dest_id.state == 'waiting':
                procurement.move_dest_id.write(
                    {'state': 'confirmed', 'procure_method': 'make_to_stock'})
        return super(ProcurementOrder, self).unlink()
