# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    valuation_differs = fields.Boolean(compute="_compute_valuation_differs")
    valuation_difference_report = fields.Html(
        compute="_compute_valuation_difference_report"
    )

    @api.depends("order_line.price_unit")
    def _compute_valuation_differs(self):
        self.valuation_differs = False
        # Other states won't change the lines costs
        for order in self.filtered(lambda x: x.state == "purchase"):
            order.valuation_differs = any(order.order_line.mapped("valuation_differs"))

    @api.depends("order_line.valuation_difference")
    def _compute_valuation_difference_report(self):
        self.valuation_difference_report = False
        for order in self.filtered("valuation_differs"):
            valuation_difference_report = ""
            for line in order.order_line.filtered("valuation_differs"):
                valuation_difference = (
                    f"{line.currency_id.round(line.valuation_difference)}"
                )
                if line.valuation_difference > 0:
                    color = "success"
                    valuation_difference = f"+{valuation_difference}"
                else:
                    color = "danger"
                valuation_difference_report += (
                    f"<li><b>{line.display_name}</b>: "
                    f"<span class='text-{color}'>{valuation_difference}</span></li>"
                )
            order.valuation_difference_report = (
                f"<ul>{valuation_difference_report}</ul>"
            )

    def action_apply_price_difference(self):
        self.ensure_one()
        if not self.valuation_differs or not self.user_has_groups(
            "purchase.group_purchase_manager"
        ):
            return
        for line in self.order_line.filtered("valuation_differs"):
            line._apply_unit_price_difference()
        self.order_line.valuation_differs = False


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    valuation_differs = fields.Boolean(compute="_compute_valuation_differs", store=True)
    valuation_difference = fields.Float(
        compute="_compute_valuation_differs", store=True
    )

    def _get_valued_in_moves(self):
        self.ensure_one()
        return self._get_po_line_moves().filtered(
            lambda m: m.state == "done" and m.product_qty != 0
        )

    @api.depends("price_subtotal", "qty_invoiced")
    def _compute_valuation_differs(self):
        """We can only propagate the cost change when there are quantities received
        and there aren't invoices"""
        self.valuation_differs = False
        # Only Average Cost (AVCO) is supported for value adjustment
        for line in self.filtered(
            lambda x: x.price_unit
            and x.qty_received
            and not x.qty_invoiced
            and x.product_id.cost_method == "average"
        ):
            (price_unit, svl_qty, price_diff, _) = line._get_valuation_diff_values()
            if (
                float_compare(
                    price_diff, 0, precision_rounding=line.currency_id.rounding
                )
                != 0
            ):
                line.valuation_differs = True
                line.valuation_difference = price_diff

    def _get_valuation_diff_values(self):
        self.ensure_one()
        moves = self._get_valued_in_moves()
        price_unit = self.price_subtotal / self.product_uom_qty
        svl_qty = sum(moves.stock_valuation_layer_ids.mapped("remaining_qty"))
        remaining_value = sum(moves.stock_valuation_layer_ids.mapped("remaining_value"))
        price_diff = (price_unit * svl_qty) - remaining_value
        return price_unit, svl_qty, price_diff, remaining_value

    def _prepare_price_difference_svl(self):
        """We might need to create an adjustment layer for the price difference when
        some of the valued units are already gone"""
        return {
            "company_id": self.company_id.id,
            "product_id": self.product_id.id,
            "quantity": 0,
            "unit_cost": 0,
            "remaining_qty": 0,
            "remaining_value": 0,
            "stock_valuation_layer_id": False,
        }

    def _prepare_pdiff_svl_vals(self, corrected_layer, price_diff):
        self.ensure_one()
        price_diff = self.currency_id.round(price_diff)
        return {
            "purchase_line_id": self.id,
            "company_id": self.company_id.id,
            "product_id": self.product_id.id,
            "quantity": 0,
            "unit_cost": 0,
            "remaining_qty": 0,
            "remaining_value": 0,
            "value": price_diff,
            "price_diff_value": price_diff,
            "stock_valuation_layer_id": corrected_layer.id,
            "description": _("Price difference layer created from %(line)s")
            % {"line": self.display_name},
        }

    def _get_purchase_line_pdiff_svl(self):
        self.ensure_one()
        return self.env["stock.valuation.layer"].search(
            [("purchase_line_id", "=", self.id)]
        )

    def _log_svl_cost_update(self, layer, msg, origin_values=None):
        """Builds the history of the costs updates for the given layer. We can tell
        who, when and what values did change"""
        previous_history = layer.cost_update_history or ""
        change = ""
        if origin_values:
            change = (
                f"value: {origin_values['value']} / "
                f"unit cost: {origin_values['unit_cost']} => "
                f"value: {layer.value} / "
                f"unit cost: {layer.unit_cost}"
            )
        return (
            f"{previous_history}"
            f"- {fields.Datetime.now()} [{self.env.user.name}]: {msg} {change}\n"
        )

    def _apply_unit_price_difference(self):
        """Fix valuation from the purchase price"""
        self.ensure_one()
        # Invalidate cache for the svl values of the product
        self.product_id.invalidate_recordset(["value_svl", "quantity_svl"])
        (
            price_unit,
            svl_qty,
            price_diff,
            remaining_value,
        ) = self._get_valuation_diff_values()
        unit_cost = price_diff / svl_qty
        moves = self._get_valued_in_moves()
        fields.first(moves.stock_valuation_layer_ids)
        for move in moves:
            valuation_layers = move.stock_valuation_layer_ids
            for layer in valuation_layers:
                origin_values, *_ = layer.read()
                # We need to fix the original values
                value = self.product_id._prepare_in_svl_vals(
                    layer.remaining_qty, unit_cost
                )["value"]
                # Avoid rounding issues getting the precise price_unit
                current_unit_cost = 0
                if layer.remaining_qty:
                    current_unit_cost = layer.remaining_value / layer.remaining_qty
                # Case for returns
                elif layer.quantity:
                    current_unit_cost = layer.value / layer.quantity
                new_layer_unit_cost = current_unit_cost + unit_cost
                if layer.value > 0:
                    layer.remaining_value += value
                    layer_remaining_qty = layer.remaining_qty + sum(
                        move.returned_move_ids.mapped("quantity_done")
                    )
                    new_layer_value = (new_layer_unit_cost * layer_remaining_qty) + (
                        layer.unit_cost * (layer.quantity - layer_remaining_qty)
                    )
                    layer.value = new_layer_unit_cost * layer.quantity
                    layer.unit_cost = new_layer_unit_cost
                    price_diff = new_layer_value - layer.value
                    if not float_is_zero(
                        price_diff, precision_rounding=self.currency_id.rounding
                    ):
                        vals = self._prepare_pdiff_svl_vals(layer, price_diff)
                        price_diff_svl = self._get_purchase_line_pdiff_svl()
                        if not price_diff_svl:
                            price_diff_svl = layer.create(vals)
                        else:
                            price_diff_svl.update(vals)
                        price_diff_svl.cost_update_history = self._log_svl_cost_update(
                            price_diff_svl,
                            f"Cost adjustment for {self.order_id.name} "
                            f"for a value of {price_diff}",
                        )
                else:
                    layer.unit_cost = new_layer_unit_cost
                    layer.value = new_layer_unit_cost * layer.quantity
                layer.cost_update_history = self._log_svl_cost_update(
                    layer,
                    f"Updated cost from {self.order_id.name}",
                    origin_values=origin_values,
                )
        # Now let's update the product cost
        product = self.product_id.with_company(self.company_id.id)
        if not float_is_zero(
            product.quantity_svl, precision_rounding=product.uom_id.rounding
        ):
            product.sudo().with_context(disable_auto_svl=True).write(
                {"standard_price": product.value_svl / product.quantity_svl}
            )
