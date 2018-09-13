# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.multi
    def _run_buy(self, product_id, product_qty, product_uom, location_id, name,
                 origin, values):
        """
            Pass in context the purchase group type for re-write
            purchase.requisition create method
        """
        purchase_requisition_group = (
            product_id.purchase_requisition_group_id or
            product_id.categ_id.purchase_requisition_group_id
        )
        my_ctx = self.with_context(grouped_by_type=purchase_requisition_group)
        return super(ProcurementRule, my_ctx)._run_buy(
            product_id, product_qty, product_uom, location_id, name, origin,
            values
        )
