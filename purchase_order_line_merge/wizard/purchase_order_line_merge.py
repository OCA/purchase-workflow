from odoo import Command, api, fields, models
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
        po_lines = self._filter_mergeable_lines(po_lines)
        # Auto-fill vendor if all selected lines belong to the same one
        res["partner_id"] = self._get_default_partner(po_lines).id
        res["line_ids"] = [
            Command.create(self._prepare_default_line_vals(line)) for line in po_lines
        ]
        return res

    @api.model
    def _filter_mergeable_lines(self, po_lines):
        """Return the purchase lines eligible for merge initialization."""
        return po_lines.filtered(lambda line: line.state != "cancel")

    @api.model
    def _get_default_partner(self, po_lines):
        """Return the vendor if all lines share the same one, else an empty one."""
        partners = po_lines.partner_id
        if len(partners) == 1:
            return partners
        return self.env["res.partner"]

    @api.model
    def _prepare_default_line_vals(self, po_line):
        """Prepare wizard line values from a purchase order line."""
        return {
            "source_line_id": po_line.id,
            "original_qty": po_line.product_qty,
            "quantity": po_line.product_qty,
            "price_unit": po_line.price_unit,
        }

    def _check_merge_allowed(self):
        self.ensure_one()
        source_orders = self.line_ids.source_line_id.order_id
        currencies = source_orders.currency_id
        if len(currencies) > 1:
            raise UserError(
                self.env._(
                    "Cannot merge lines with different currencies. "
                    "Please select lines with the same currency."
                )
            )
        picking_types = source_orders.picking_type_id
        if len(picking_types) > 1:
            raise UserError(
                self.env._(
                    "Cannot merge lines from different warehouses. "
                    "Please select lines with the same warehouse."
                )
            )

    def _get_lines_to_merge(self):
        """Return wizard lines that pass merge validation."""
        return self.line_ids.filtered(lambda line: line._is_mergeable())

    def action_merge(self):
        self.ensure_one()
        self._check_merge_allowed()
        lines_to_merge = self._get_lines_to_merge()
        if not lines_to_merge:
            raise UserError(
                self.env._("No lines with quantity greater than zero to merge.")
            )
        order_vals = self._prepare_purchase_order_vals()
        order_vals["order_line"] = [
            Command.create(vals)
            for vals in self._prepare_purchase_order_line_vals(lines_to_merge)
        ]
        new_order = self.env["purchase.order"].create(order_vals)
        self._update_source_line_quantities(lines_to_merge)
        self._cancel_empty_source_orders()
        return new_order.with_context(create=False)._get_records_action(
            name=self.env._("Purchase Order")
        )

    def _update_source_line_quantities(self, lines_to_merge):
        """Update source purchase lines with remaining quantities after merge."""
        for line in lines_to_merge:
            remaining = line.original_qty - line.quantity
            line.source_line_id.write({"product_qty": remaining})

    def _cancel_empty_source_orders(self):
        """Cancel source purchase orders whose total becomes zero."""
        source_orders = self.line_ids.source_line_id.order_id
        orders_to_cancel = source_orders.filtered(lambda order: order.amount_total == 0)
        orders_to_cancel.button_cancel()

    def _prepare_purchase_order_vals(self):
        self.ensure_one()
        source_orders = self.line_ids.source_line_id.order_id
        return {
            "partner_id": self.partner_id.id,
            "date_order": self.date_order,
            "origin": ", ".join(source_orders.mapped("name")),
            "currency_id": source_orders[0].currency_id.id,
            "picking_type_id": source_orders[0].picking_type_id.id,
        }

    def _prepare_purchase_order_line_vals(self, lines):
        """Group the given wizard lines and return the order lines to create."""
        self.ensure_one()
        merged = {}
        for line in lines:
            key = line._get_merge_key()
            if key not in merged:
                merged[key] = {
                    "product_id": line.product_id.id,
                    "name": line.product_id.display_name,
                    "product_uom": line.product_uom.id,
                    "product_qty": 0.0,
                    "price_unit": line.price_unit,
                    "date_planned": self.date_order,
                    "taxes_id": [Command.set(line.taxes_id.ids)],
                    "discount": line.discount,
                }
            merged[key]["product_qty"] += line.quantity
        return list(merged.values())


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
    discount = fields.Float(
        related="source_line_id.discount",
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

    @api.depends("quantity", "price_unit", "discount")
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = (
                line.quantity * line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            )

    def _get_merge_key(self):
        self.ensure_one()
        return (
            self.product_id.id,
            self.price_unit,
            self.product_uom.id,
            tuple(sorted(self.taxes_id.ids)),
            self.discount,
        )

    def _is_mergeable(self):
        """Return True when this line should be included in merge processing."""
        self.ensure_one()
        # Hook for line-level rules.
        # In inherited modules, raise UserError("...") here to provide a
        # custom validation message for this line.
        return self.quantity > 0
