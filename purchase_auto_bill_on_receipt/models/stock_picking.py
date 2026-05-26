# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    auto_bill_pending = fields.Boolean(
        copy=False,
        help="Set when a validated receipt or return is queued for "
        "auto-billing. The scheduled action picks it up to create and post "
        "the Vendor Bill or Credit Note.",
    )

    def _auto_create_vendor_bill(self):
        self.ensure_one()
        self.auto_bill_pending = False
        purchase = self.purchase_id
        if not purchase or not purchase._auto_bill_enabled():
            return
        purchase._auto_bill_for_picking(self)

    def _cron_auto_bill(self):
        for picking in self.search([("auto_bill_pending", "=", True)]):
            try:
                with self.env.cr.savepoint():
                    picking._auto_create_vendor_bill()
            except Exception:
                _logger.exception("Failed to auto-bill picking %s", picking.name)

    def button_validate(self):
        res = super().button_validate()
        to_process = self.filtered(
            lambda p: p.state == "done"
            and p.purchase_id
            and p.purchase_id._auto_bill_enabled()
            and (
                p.picking_type_code == "incoming"
                or any(m.to_refund for m in p.move_ids if m.purchase_line_id)
            )
        )
        if to_process:
            to_process.auto_bill_pending = True
            self.env.ref(
                "purchase_auto_bill_on_receipt.ir_cron_auto_bill"
            ).sudo()._trigger()
        return res
