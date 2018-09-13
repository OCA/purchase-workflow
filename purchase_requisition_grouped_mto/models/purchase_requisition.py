# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.osv.expression import is_leaf


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    def _find_grouping_target_domain(self, grouped_by_type, vals):
        return [
            ('type_id', '=', grouped_by_type.id),
            ('state', '=', 'draft'),
        ]

    def _find_grouping_target(self, grouped_by_type, vals):
        return self.search(
            self._find_grouping_target_domain(grouped_by_type, vals), limit=1)

    @api.model
    def create(self, vals):
        """
            Search if exists any purchase_requisition with this type. If
            exists add lines instead of create one and update the origin field
            with the new origin
        """
        grouped_by_type = self.env.context.get('grouped_by_type', False)
        if grouped_by_type:
            vals['type_id'] = grouped_by_type.id
            purchase_requisition = self._find_grouping_target(
                grouped_by_type, vals)
            if purchase_requisition:
                vals_update = {
                    'line_ids': vals['line_ids'],
                }
                if not vals['origin'] in purchase_requisition.origin:
                    vals_update['origin'] = '{}, {}'.format(
                        purchase_requisition.origin, vals['origin'])
                purchase_requisition.write(vals_update)
                return purchase_requisition
        return super(PurchaseRequisition, self).create(vals)

    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Purchase requisition origin field has all origins
        if 'grouped_by_type' in self.env.context:
            for i, arg in enumerate(args):
                if (is_leaf(arg) and isinstance(arg[0], str) and
                        arg[0] == 'origin'):
                    args[i] = (arg[0], 'like', arg[2])
                    break
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count)
