# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo import Command, fields, models

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    block_auto_bill = fields.Boolean(
        help="When enabled, suppresses automatic bill creation on receipt "
        "for this order, regardless of the company or vendor settings.",
    )

    def _auto_bill_enabled(self):
        self.ensure_one()
        if self.block_auto_bill:
            return False
        partner_setting = self.partner_id.commercial_partner_id.auto_bill_on_receipt
        if partner_setting == "auto":
            return True
        if partner_setting == "no_auto":
            return False
        return self.company_id.auto_bill_on_receipt

    def _auto_bill_log_failure(
        self, picking, step, exception, bill=False, refund=False
    ):
        self.ensure_one()
        doc = self.env._("credit note") if refund else self.env._("bill")
        src = self.env._("return") if refund else self.env._("receipt")
        if step == "create":
            summary = self.env._(
                "Auto %(doc)s creation failed — manual review needed",
                doc=doc,
            )
            body = self.env._(
                "Auto %(doc)s creation failed on %(src)s %(picking)s: %(error)s",
                doc=doc,
                src=src,
                picking=picking.name,
                error=exception,
            )
        else:
            summary = self.env._(
                "Auto %(doc)s posting failed — manual review needed",
                doc=doc,
            )
            body = self.env._(
                "Auto %(doc)s posting failed on %(src)s %(picking)s "
                "(%(doc)s %(bill)s remains in draft): %(error)s",
                doc=doc,
                src=src,
                picking=picking.name,
                bill=bill.display_name if bill else "",
                error=exception,
            )
        self.message_post(body=body, message_type="notification")
        self.activity_schedule(
            "mail.mail_activity_data_todo",
            summary=summary,
            user_id=(self.user_id or self.env.user).id,
        )

    def _get_picking_line_qty(self, picking, line, refund=False):
        self.ensure_one()
        qty = 0.0
        moves = picking.move_ids.filtered(lambda m: m.purchase_line_id == line)
        if refund:
            moves = moves.filtered("to_refund")
        for move in moves:
            qty += move.product_uom._compute_quantity(
                move.quantity, line.product_uom_id
            )
        return qty

    def _auto_bill_create(self, picking, eligible_lines, refund=False):
        self.ensure_one()
        move_type = "in_refund" if refund else "in_invoice"
        invoice_vals = self.with_context(default_move_type=move_type)._prepare_invoice()
        # Billing runs under the cron user, whose timezone is unreliable, so
        # derive the bill date from the company partner's timezone instead.
        tz = self.company_id.partner_id.tz or "UTC"
        invoice_vals["invoice_date"] = fields.Date.context_today(
            self.with_context(tz=tz), picking.date_done
        )
        invoice_lines = []
        sequence = 10
        pending_section = None
        for line in self.order_line:
            if line.display_type in ("line_section", "line_subsection"):
                pending_section = line
                continue
            if line not in eligible_lines:
                continue
            picking_qty = self._get_picking_line_qty(picking, line, refund=refund)
            if refund:
                qty = min(picking_qty, abs(line.qty_to_invoice))
            else:
                qty = min(picking_qty, line.qty_to_invoice)
            if qty <= 0:
                continue
            if pending_section:
                section_vals = pending_section._prepare_account_move_line()
                section_vals["sequence"] = sequence
                invoice_lines.append(Command.create(section_vals))
                sequence += 1
                pending_section = None
            line_vals = line._prepare_account_move_line()
            line_vals["quantity"] = qty
            line_vals["sequence"] = sequence
            invoice_lines.append(Command.create(line_vals))
            sequence += 1
        invoice_vals["invoice_line_ids"] = invoice_lines
        return (
            self.env["account.move"]
            .with_company(self.company_id)
            .with_context(default_move_type=move_type)
            .create(invoice_vals)
        )

    def _is_return_picking(self, picking):
        return picking.picking_type_code != "incoming" and any(
            m.to_refund for m in picking.move_ids if m.purchase_line_id
        )

    def _auto_bill_for_picking(self, picking):
        self.ensure_one()
        refund = self._is_return_picking(picking)
        moves = picking.move_ids
        if refund:
            moves = moves.filtered("to_refund")
        eligible_lines = moves.purchase_line_id.filtered(
            lambda line: line.product_id.purchase_method == "receive"
            and (line.qty_to_invoice < 0 if refund else line.qty_to_invoice > 0)
        )
        if not eligible_lines:
            return self.env["account.move"]
        try:
            # Isolate the create in a savepoint: a database-level error aborts
            # the cursor, and we must roll back to a clean state before the
            # failure logging below can write to it.
            with self.env.cr.savepoint():
                bill = self._auto_bill_create(picking, eligible_lines, refund=refund)
        except Exception as e:
            _logger.exception(
                "Auto-%s creation failed for PO %s / picking %s",
                "refund" if refund else "bill",
                self.name,
                picking.name,
            )
            self._auto_bill_log_failure(picking, "create", e, refund=refund)
            return self.env["account.move"]
        try:
            with self.env.cr.savepoint():
                bill.action_post()
        except Exception as e:
            _logger.exception(
                "Auto-%s posting failed for PO %s / picking %s / %s",
                "refund" if refund else "bill",
                self.name,
                picking.name,
                bill.name,
            )
            self._auto_bill_log_failure(picking, "post", e, bill=bill, refund=refund)
        return bill
