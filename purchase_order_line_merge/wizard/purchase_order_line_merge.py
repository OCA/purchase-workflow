from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderLineMerge(models.TransientModel):
    _name = "purchase.order.line.merge"
    _description = "Merge Purchase Order Lines"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
        required=True,
    )
    date_order = fields.Datetime(
        string="Order Date",
        required=True,
        default=fields.Datetime.now,
    )
    line_ids = fields.One2many(
        comodel_name="purchase.order.line.merge.line",
        inverse_name="wizard_id",
        string="Lines",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get("active_ids", [])
        if not active_ids:
            return res
        po_lines = self.env["purchase.order.line"].browse(active_ids)
        res["partner_id"] = self._get_default_partner(po_lines)
        line_vals = []
        for line in po_lines:
            line_vals.append(
                (
                    0,
                    0,
                    self._prepare_default_line_vals(line),
                )
            )
        res["line_ids"] = line_vals
        return res

    @api.model
    def _get_default_partner(self, po_lines):
        """Return the vendor id if all lines share the same one, else False."""
        partners = po_lines.mapped("partner_id")
        if len(partners) == 1:
            return partners.id
        return False

    @api.model
    def _prepare_default_line_vals(self, po_line):
        """Prepare wizard line values from a purchase order line.

        Default quantity is the available amount considering both
        invoiced and received quantities. If the line is already fully
        invoiced or fully received, the quantity defaults to zero.
        """
        available_qty = po_line.product_qty - max(
            po_line.qty_invoiced, po_line.qty_received
        )
        return {
            "source_line_id": po_line.id,
            "original_qty": po_line.product_qty,
            "quantity": max(0.0, available_qty),
            "price_unit": po_line.price_unit,
        }

    def _check_merge_allowed(self):
        self.ensure_one()
        source_orders = self.line_ids.mapped("source_line_id.order_id")
        invalid_orders = source_orders.filtered(lambda o: o.state in ("done", "cancel"))
        if invalid_orders:
            raise UserError(
                self.env._(
                    "Cannot merge lines from locked or cancelled orders: %s.",
                    ", ".join(invalid_orders.mapped("name")),
                )
            )
        currencies = source_orders.mapped("currency_id")
        if len(currencies) > 1:
            raise UserError(
                self.env._(
                    "Cannot merge lines with different currencies. "
                    "Please select lines with the same currency."
                )
            )
        picking_types = source_orders.mapped("picking_type_id")
        if len(picking_types) > 1:
            raise UserError(
                self.env._(
                    "Cannot merge lines from different warehouses. "
                    "Please select lines with the same warehouse."
                )
            )
        for line in self.line_ids:
            if line.quantity < 0:
                raise UserError(
                    self.env._(
                        "Quantity cannot be negative. "
                        "Check the line for product: %(product)s (PO: %(po)s).",
                        product=line.product_id.display_name,
                        po=line.source_line_id.order_id.name,
                    )
                )
            if line.quantity > line.original_qty:
                raise UserError(
                    self.env._(
                        "Quantity to merge cannot exceed the original quantity. "
                        "Check the line for product: %(product)s, "
                        "quantity: %(qty)s (PO: %(po)s).",
                        product=line.product_id.display_name,
                        qty=line.quantity,
                        po=line.source_line_id.order_id.name,
                    )
                )
            remaining = line.original_qty - line.quantity
            src = line.source_line_id
            if remaining < src.qty_received:
                raise UserError(
                    self.env._(
                        "Cannot merge %(qty)s units of %(product)s "
                        "(PO: %(po)s). The remaining quantity "
                        "(%(remaining)s) would be less than the already "
                        "received quantity (%(received)s).",
                        qty=line.quantity,
                        product=line.product_id.display_name,
                        po=src.order_id.name,
                        remaining=remaining,
                        received=src.qty_received,
                    )
                )

    def action_merge(self):
        self.ensure_one()
        self._check_merge_allowed()
        lines_to_merge = self.line_ids.filtered(lambda ln: ln.quantity > 0)
        if not lines_to_merge:
            raise UserError(
                self.env._("No lines with quantity greater than zero to merge.")
            )
        merged = {}
        for line in lines_to_merge:
            key = line._get_merge_key()
            if key not in merged:
                merged[key] = {
                    "product_id": line.product_id,
                    "price_unit": line.price_unit,
                    "product_uom": line.product_uom,
                    "taxes_id": line.taxes_id,
                    "quantity": 0.0,
                }
            merged[key]["quantity"] += line.quantity
        order_vals = self._prepare_purchase_order_vals()
        order_vals["order_line"] = [
            (0, 0, self._prepare_purchase_order_line_vals(vals))
            for vals in merged.values()
        ]
        new_order = self.env["purchase.order"].create(order_vals)
        for line in self.line_ids:
            remaining = line.original_qty - line.quantity
            line.source_line_id.write({"product_qty": remaining})
        source_orders = self.line_ids.mapped("source_line_id.order_id")
        orders_to_cancel = source_orders.filtered(lambda o: o.amount_total == 0)
        orders_to_cancel.button_cancel()
        return self._action_view_purchase_order(new_order)

    def _prepare_purchase_order_vals(self):
        self.ensure_one()
        source_orders = self.line_ids.mapped("source_line_id.order_id")
        return {
            "partner_id": self.partner_id.id,
            "payment_term_id": (self.partner_id.property_supplier_payment_term_id.id),
            "date_order": self.date_order,
            "origin": ", ".join(source_orders.mapped("name")),
            "currency_id": source_orders[0].currency_id.id,
            "picking_type_id": source_orders[0].picking_type_id.id,
        }

    def _prepare_purchase_order_line_vals(self, vals):
        return {
            "product_id": vals["product_id"].id,
            "name": vals["product_id"].display_name,
            "product_uom": vals["product_uom"].id,
            "product_qty": vals["quantity"],
            "price_unit": vals["price_unit"],
            "date_planned": self.date_order,
            "taxes_id": [(6, 0, vals["taxes_id"].ids)],
        }

    def _action_view_purchase_order(self, purchase_order):
        action = {
            "name": self.env._("Purchase Order"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "context": {"create": False},
        }
        if len(purchase_order) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": purchase_order.id,
                }
            )
        else:
            action.update(
                {
                    "view_mode": "list,form",
                    "domain": [("id", "in", purchase_order.ids)],
                }
            )
        return action


class PurchaseOrderLineMergeLine(models.TransientModel):
    _name = "purchase.order.line.merge.line"
    _description = "Purchase Order Line Merge Line"

    wizard_id = fields.Many2one(
        comodel_name="purchase.order.line.merge",
        required=True,
        ondelete="cascade",
    )
    source_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Source Line",
        required=True,
        readonly=True,
    )
    order_id = fields.Many2one(
        related="source_line_id.order_id",
    )
    product_id = fields.Many2one(
        related="source_line_id.product_id",
    )
    product_uom = fields.Many2one(
        related="source_line_id.product_uom",
    )
    price_unit = fields.Float(
        string="Unit Price",
        digits="Product Price",
    )
    taxes_id = fields.Many2many(
        related="source_line_id.taxes_id",
    )
    qty_invoiced = fields.Float(
        related="source_line_id.qty_invoiced",
    )
    qty_received = fields.Float(
        related="source_line_id.qty_received",
    )
    original_qty = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
    )
    quantity = fields.Float(
        string="Quantity to Merge",
        digits="Product Unit of Measure",
    )
    price_subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_price_subtotal",
    )

    @api.depends("quantity", "price_unit")
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

    def _get_merge_key(self):
        self.ensure_one()
        return (
            self.product_id.id,
            self.price_unit,
            self.product_uom.id,
            tuple(sorted(self.taxes_id.ids)),
        )
