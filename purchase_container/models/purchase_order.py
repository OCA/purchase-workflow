from odoo import Command, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    container_ids = fields.Many2many(
        "purchase.container",
        string="Containers",
        compute="_compute_container_ids",
        inverse="_inverse_container_ids",
        copy=False,
        store=True,
        index=True,
    )

    @api.depends("picking_ids.container_id")
    def _compute_container_ids(self):
        for purchase in self:
            if purchase.picking_ids:
                purchase.container_ids = [
                    Command.set(purchase.picking_ids.container_id.ids)
                ]

    def _inverse_container_ids(self):
        pass

    def _prepare_picking(self):
        # This function initialize the picking vals from the current order
        vals = super()._prepare_picking()
        # So if we have at least a container set on the order, we should
        # initialize the picking container with one.
        if self.container_ids:
            # Arbitrarily, we take the first one by default
            vals["container_id"] = self.container_ids[0].id
        return vals
