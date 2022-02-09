# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, fields, models
from odoo.tools.float_utils import float_compare


class PurchaseOrderManualReceipt(models.TransientModel):
    _name = "purchase.order.manual.receipt.wizard"
    _description = "PO Manual Receipt Wizard"

    line_ids = fields.One2many(
        "purchase.order.manual.receipt.wizard.line",
        "wizard_id",
    )

    auto_confirm_picking = fields.Boolean(
        default=True, help="Automatically confirms the picking after creation."
    )

    checks_result = fields.Selection(
        [("success", "Success"), ("failure", "Failure")],
        default="success",
    )

    checks_result_msg = fields.Text(
        help="Stores error messages result from executed checks"
    )

    purchase_order_id = fields.Many2one(
        "purchase.order",
        required=True,
    )

    scheduled_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
    )

    #######################
    # BUTTONS AND ACTIONS #
    #######################

    def open_form_view(self):
        self.ensure_one()
        return {
            "name": _("Manual Receipt"),
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "res_model": "purchase.order.manual.receipt.wizard",
            "target": "new",
            "view_mode": "form",
        }

    def open_picking_form_view(self, picking):
        self.ensure_one()
        return {
            "name": _("Picking"),
            "type": "ir.actions.act_window",
            "res_id": picking.id,
            "res_model": "stock.picking",
            "view_mode": "form",
        }

    def button_check(self):
        """Runs checks on the wizard data, then opens the wizard again"""
        self.ensure_one()
        errs = self._execute_all_checks()
        self.write(self._prepare_post_check_vals(errs))
        return self.open_form_view()

    def button_confirm(self):
        """Confirms wizard data and creates new picking"""
        self.ensure_one()
        # Setting `checks_result` to "success" because the user is allowed to
        # ignore warnings; then, we'll run pre-confirm checks and, if any of
        # them fails, field `checks_result` should be changed
        self.checks_result = "success"
        errs = self._execute_pre_confirm_checks()
        self.write(self._prepare_post_check_vals(errs))
        if self.checks_result != "success":
            # Some pre-confirm check failed: reopen the wizard
            self.checks_result_msg += _("\n\nThese checks cannot be skipped!")
            return self.open_form_view()
        # Create picking and picking's open form view
        return self.open_picking_form_view(self._generate_picking())

    ####################################
    # CHECKS AND CHECK-RELATED METHODS #
    ####################################

    def _execute_pre_confirm_checks(self) -> dict:
        """Executes pre-confirm checks on wizard data

        Returns a dict mapping each check to its error message (even if empty,
        which means the check was successful)
        """
        self.ensure_one()
        return {"_check_lines_consistency": self._check_lines_consistency()}

    def _execute_all_checks(self) -> dict:
        """Executes checks on wizard data

        Returns a dict mapping each check to its error message (even if empty,
        which means the check was successful)
        """
        self.ensure_one()
        return {
            "_check_lines_consistency": self._check_lines_consistency(),
            "_check_product_quantities": self._check_product_quantities(),
        }

    def _prepare_post_check_vals(self, errors: dict) -> dict:
        """Prepares `write` vals to update wizard after executing checks

        :param dict errors: dict mapping each check name to its error
        """
        res, msg = "success", ""
        if any(errors.values()):
            res, msg = "failure", "\n\n".join(m for m in errors.values() if m)
        return {"checks_result": res, "checks_result_msg": msg}

    def _check_lines_consistency(self) -> str:
        """Lines consistency check"""
        self.ensure_one()
        err = ""
        if not self.line_ids or any(line.qty < 0 for line in self.line_ids):
            err = _(
                "Receipts must have at least 1 line and every line must have"
                " strictly positive quantity."
            )
        return err

    def _check_product_quantities(self) -> str:
        """Receivable/to receive quantities check"""
        self.ensure_one()
        err = ""
        if self.line_ids:
            prec = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            mtr = [
                (pid, qtr, rq)
                for (pid, qtr, rq) in self._get_product_quantities_info()
                if float_compare(qtr, rq, prec) == 1
            ]
            if mtr:
                msg = [_("Qty to receive exceeds the receivable qty:")]
                for pid, q1, q2 in mtr:
                    prod = self.env["product.product"].browse(pid)
                    uom_name = prod.uom_po_id.name
                    msg.append(
                        _("- {p}: to receive {q1} {u}, receivable {q2} {u}").format(
                            p=prod.name, q1=q1, q2=q2, u=uom_name
                        )
                    )
                err = "\n".join(msg)
        return err

    def _get_product_quantities_info(self) -> list:
        """Returns list of triplet (prod.id, qty to receive, receivable qty)"""
        self.ensure_one()
        receivable = self._get_product_quantities_info_receivable()
        to_receive = self._get_product_quantities_info_to_receive()
        return [
            (pid, to_receive.get(pid, 0), receivable.get(pid, 0))
            for pid in set(to_receive.keys()).union(receivable.keys())
        ]

    def _get_product_quantities_info_receivable(self) -> dict:
        """Returns mapping {prod: receivable qty}

        Qty is retrieved from the purchase line's `manually_receivable_qty`
        field, so it's in product's PO UoM
        """
        self.ensure_one()
        receivable = defaultdict(float)
        for po_line in self.line_ids.purchase_line_id:
            prod, qty = po_line.product_id, po_line.manually_receivable_qty
            receivable[prod.id] += qty
        return receivable

    def _get_product_quantities_info_to_receive(self) -> dict:
        """Returns mapping {prod: qty to receive}

        Qty is retrieved from the wizard line's `qty` and is converted into
        product's PO UoM for consistency with
        `_get_product_quantities_info_receivable()` (this allows comparing data
        faster when the two mappings are used together)
        """
        self.ensure_one()
        to_receive = defaultdict(float)
        for line in self.line_ids:
            qty = line.qty
            from_uom = line.uom_id
            prod = line.product_id
            to_uom = prod.uom_po_id
            to_receive[prod.id] += from_uom._compute_quantity(qty, to_uom, round=False)
        return to_receive

    ##############################
    # PICKING GENERATION METHODS #
    ##############################

    def _generate_picking(self):
        """Creates picking

        Also manages confirmation and validation if related fields are flagged
        """
        self.ensure_one()
        vals = self._get_picking_vals()
        vals["move_lines"] = [(0, 0, v) for v in self._get_move_vals_list()]
        picking = self.env["stock.picking"].create(vals)
        if self.auto_confirm_picking:
            picking.action_confirm()
        return picking

    def _get_picking_vals(self) -> dict:
        """Prepares `stock.picking.create()` vals"""
        self.ensure_one()
        order = self.purchase_order_id
        order = order.with_company(order.company_id)
        # Use `purchase.order` utilities to create picking data properly,
        # then just update the picking values according to wizard
        picking_vals = order._prepare_picking()
        picking_vals["scheduled_date"] = self.scheduled_date
        return picking_vals

    def _get_move_vals_list(self) -> list:
        """Returns list of `stock.move.create()` values"""
        self.ensure_one()
        return self.line_ids._get_move_vals_list()
