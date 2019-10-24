# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def unlink(self):
        for line in self:
            line.procurement_ids.filtered(lambda r: r.state != 'cancel').unlink()
        res = super(PurchaseOrderLine, self).unlink()
        return res


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
