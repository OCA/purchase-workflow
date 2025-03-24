# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateManualStockPickingWizard(models.TransientModel):
    _name = "create.stock.picking.wizard"
    _description = "Create Manual Stock Picking Wizard"

    def _default_purchase_order(self):
        if self.env.context["active_model"] == "purchase.order.line":
            return (
                self.env["purchase.order.line"]
                .browse(self.env.context["active_ids"][0])
                .order_id
            )
        return self.env["purchase.order"].browse(self.env.context["active_id"])

    def _default_location_dest_id(self):
        return self.env["stock.location"].browse(
            self._default_purchase_order()._get_destination_location()
        )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        active_model = self.env.context["active_model"]
        if active_model == "purchase.order.line":
            po_line_ids = self.env.context["active_ids"] or []
            purchase_lines = (
                self.env["purchase.order.line"]
                .browse(po_line_ids)
                .filtered(
                    lambda p: p.product_id.type == "consu" and p.pending_to_receive
                )
            )
        elif active_model == "purchase.order":
            po_ids = self.env.context["active_ids"] or []
            purchase_lines = (
                self.env["purchase.order"]
                .browse(po_ids)
                .mapped("order_line")
                .filtered(
                    lambda p: p.product_id.type == "consu" and p.pending_to_receive
                )
            )
        self._check_purchase_line_constrains(purchase_lines)
        res["line_ids"] = self.fill_lines(purchase_lines)
        res["partner_id"] = purchase_lines.mapped("order_id.partner_id").id
        return res

    def _check_purchase_line_constrains(self, purchase_lines):
        if len(purchase_lines.mapped("order_id.partner_id")) > 1:
            raise UserError(_("Please select one partner at a time"))
        if len(purchase_lines.mapped("order_id")) > 1:
            raise UserError(_("Please select one purchase order at a time"))

    def fill_lines(self, po_lines):
        lines = [
            (
                0,
                0,
                {
                    "purchase_order_line_id": line.id,
                    "name": line.name,
                    "remaining_qty": line.product_qty
                    - (line.qty_in_receipt + line.qty_received),
                    "qty": line.product_qty - (line.qty_in_receipt + line.qty_received),
                },
            )
            for line in po_lines
        ]
        return lines

    purchase_id = fields.Many2one(
        "purchase.order",
        string="Purchase Order",
        readonly=True,
        default=_default_purchase_order,
    )
    line_ids = fields.One2many(
        comodel_name="create.stock.picking.wizard.line",
        inverse_name="wizard_id",
        string="Lines",
    )
    picking_id = fields.Many2one("stock.picking", string="Stock Picking")
    partner_id = fields.Many2one("res.partner", "Vendor")
    scheduled_date = fields.Datetime(
        "Scheduled Date", related="picking_id.scheduled_date"
    )
    location_dest_id = fields.Many2one(
        "stock.location",
        "Destination Location",
        default=_default_location_dest_id,
        help="Location where the system will stock the received products.",
    )

    @api.onchange("picking_id")
    def onchange_picking_id(self):
        if self.picking_id:
            self.location_dest_id = self.picking_id.location_dest_id

    def _prepare_picking(self):
        res = self.purchase_id._prepare_picking()
        if self.location_dest_id:
            res["location_dest_id"] = self.location_dest_id.id
        return res

    def create_stock_picking(self):
        StockPicking = self.env["stock.picking"]

        # If a picking has been selected, we add products to the picking
        # otherwise we create a new picking
        picking_id = self.picking_id
        if not picking_id:
            res = self._prepare_picking()
            picking_id = StockPicking.create(res)

        # Check quantity is not above remaining quantity
        if any(line.qty > line.remaining_qty for line in self.line_ids):
            raise UserError(
                _(
                    "You can not receive more than the remaining "
                    "quantity. If you need to do so, please edit "
                    "the purchase order first."
                )
            )
        moves = self.line_ids._create_stock_moves(picking_id)
        moves = moves.filtered(
            lambda x: x.state not in ("done", "cancel")
        )._action_confirm()
        seq = 0
        for move in sorted(moves, key=lambda move: move.date_deadline or move.date):
            seq += 5
            move.sequence = seq
        moves._action_assign()
        picking_id.message_post_with_source(
            "mail.message_origin_link",
            render_values={"self": picking_id, "origin": self.purchase_id},
            subtype_xmlid="mail.mt_note",
        )

        return {
            "name": _("Stock Picking"),
            "view_mode": "form",
            "res_model": "stock.picking",
            "view_id": self.env.ref("stock.view_picking_form").id,
            "res_id": picking_id.id,
            "type": "ir.actions.act_window",
        }


class CreateManualStockPickingWizardLine(models.TransientModel):
    _name = "create.stock.picking.wizard.line"
    _description = "Create Manual Stock Picking Wizard Line"

    wizard_id = fields.Many2one(
        string="Wizard",
        comodel_name="create.stock.picking.wizard",
        required=True,
        ondelete="cascade",
    )
    purchase_order_line_id = fields.Many2one("purchase.order.line")
    name = fields.Text(string="Description", readonly=True)
    product_id = fields.Many2one(
        "product.product",
        related="purchase_order_line_id.product_id",
        string="Product",
    )
    product_uom = fields.Many2one(
        "uom.uom",
        related="purchase_order_line_id.product_uom",
        string="Unit of Measure",
    )
    date_planned = fields.Datetime(related="purchase_order_line_id.date_planned")
    product_qty = fields.Float(
        string="Quantity",
        related="purchase_order_line_id.product_qty",
        digits="Product Unit of Measure",
    )
    qty_in_receipt = fields.Float(
        related="purchase_order_line_id.qty_in_receipt",
        digits="Product Unit of Measure",
    )
    qty_received = fields.Float(
        related="purchase_order_line_id.qty_received",
        digits="Product Unit of Measure",
    )
    remaining_qty = fields.Float(
        string="Remaining Quantity",
        compute="_compute_remaining_qty",
        digits="Product Unit of Measure",
    )
    qty = fields.Float(
        string="Quantity to Receive",
        digits="Product Unit of Measure",
        help="This is the quantity taken into account to create the picking",
    )
    price_unit = fields.Float(
        related="purchase_order_line_id.price_unit",
    )
    currency_id = fields.Many2one(
        "res.currency", related="purchase_order_line_id.currency_id"
    )
    partner_id = fields.Many2one(
        "res.partner",
        related="purchase_order_line_id.partner_id",
        string="Vendor",
    )
    taxes_id = fields.Many2many(
        "account.tax", related="purchase_order_line_id.taxes_id"
    )

    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.product_qty - (
                line.qty_in_receipt + line.qty_received
            )

    def _prepare_stock_moves(self, picking):
        po_line = self.purchase_order_line_id
        return po_line._prepare_stock_moves(picking)

    def _create_stock_moves(self, picking):
        values = []
        for line in self:
            for val in line._prepare_stock_moves(picking):
                if val.get("product_uom_qty", False):
                    # CHECK ME: We can receive more than one move
                    product_uom = (
                        self.env["uom.uom"].browse(val.get("product_uom", 0))
                        or line.product_uom
                    )
                    val["product_uom_qty"] = line.product_uom._compute_quantity(
                        line.qty,
                        product_uom,
                        rounding_method="HALF-UP",
                    )
                if (
                    val.get("location_dest_id", False)
                    and not line.wizard_id.picking_id
                    and line.wizard_id.location_dest_id
                ):
                    val["location_dest_id"] = line.wizard_id.location_dest_id.id
                values.append(val)
        return self.env["stock.move"].create(values)
