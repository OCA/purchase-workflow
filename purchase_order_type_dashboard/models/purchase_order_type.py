# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderType(models.Model):
    _inherit = "purchase.order.type"

    purchase_order_ids = fields.One2many(
        comodel_name="purchase.order",
        inverse_name="order_type",
        string="Purchase Orders",
    )
    state_rfq_po_count = fields.Integer(string="RFQs", compute="_compute_po_counts")
    invoice_status_no_po_count = fields.Integer(
        string="Nothing to Bill", compute="_compute_po_counts"
    )
    invoice_status_ti_po_count = fields.Integer(
        string="Waiting Bills", compute="_compute_po_counts"
    )

    @api.depends(
        "purchase_order_ids",
        "purchase_order_ids.state",
        "purchase_order_ids.invoice_status",
    )
    def _compute_po_counts(self):
        rfq_states = ("draft", "sent", "to approve")
        po_states = ("purchase", "done")
        PurchaseOrder = self.env["purchase.order"]
        fetch_data = PurchaseOrder.read_group(
            [("order_type", "in", self.ids)],
            ["order_type", "state", "invoice_status"],
            ["order_type", "state", "invoice_status"],
            lazy=False,
        )
        result = [
            [
                data["order_type"][0],
                data["state"],
                data["invoice_status"],
                data["__count"],
            ]
            for data in fetch_data
        ]
        for order in self:
            order.state_rfq_po_count = sum(
                [r[3] for r in result if r[0] == order.id and r[1] in rfq_states]
            )
            order.invoice_status_no_po_count = sum(
                [
                    r[3]
                    for r in result
                    if r[0] == order.id and r[1] in po_states and r[2] == "no"
                ]
            )
            order.invoice_status_ti_po_count = sum(
                [r[3] for r in result if r[0] == order.id and r[2] == "to invoice"]
            )
