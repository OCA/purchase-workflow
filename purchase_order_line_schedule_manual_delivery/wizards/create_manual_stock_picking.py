# Copyright 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class CreateManualStockPickingWizard(models.TransientModel):
    _inherit = "create.stock.picking.wizard"

    @api.model
    def default_get(self, fields):
        res = super(CreateManualStockPickingWizard, self).default_get(fields)
        purchase_lines = self.env["purchase.order.line"]
        active_model = self.env.context["active_model"]
        if active_model == "purchase.order.line":
            po_line_ids = self.env.context["active_ids"] or []
            purchase_lines = (
                self.env["purchase.order.line"]
                .browse(po_line_ids)
                .filtered(
                    lambda p: p.product_id.type in ["product", "consu"]
                    and p.pending_to_receive
                )
            )
        elif active_model == "purchase.order":
            po_ids = self.env.context["active_ids"] or []
            purchase_lines = (
                self.env["purchase.order"]
                .browse(po_ids)
                .mapped("order_line")
                .filtered(
                    lambda p: p.product_id.type in ["product", "consu"]
                    and p.pending_to_receive
                )
            )
        self._check_purchase_line_constrains(purchase_lines)
        res["schedule_line_ids"] = self.fill_schedule_lines(
            purchase_lines.mapped("schedule_line_ids")
        )
        return res

    def fill_schedule_lines(self, schedule_lines):
        lines = [
            (
                0,
                0,
                {
                    "schedule_line_id": line.id,
                    "name": line.order_line_id.name,
                    "product_id": line.product_id.id,
                    "date_planned": line.date_planned,
                    "price_unit": line.order_line_id.price_unit,
                    "product_qty": line.product_qty,
                    "qty_in_receipt": line.qty_in_receipt,
                    "remaining_qty": line.product_qty
                    - line.qty_in_receipt
                    - line.qty_received,
                    "qty": line.product_qty - line.qty_in_receipt - line.qty_received,
                    "product_uom": line.order_line_id.product_uom.id,
                    "currency_id": line.order_line_id.currency_id.id,
                    "partner_id": line.order_line_id.partner_id.id,
                },
            )
            for line in schedule_lines.sorted(lambda l: l.date_planned)
        ]
        return lines

    schedule_line_ids = fields.One2many(
        comodel_name="create.stock.picking.wizard.schedule.line",
        inverse_name="wizard_id",
        string="Lines",
    )

    def create_stock_picking(self):
        return super(
            CreateManualStockPickingWizard, self.with_context(use_shedule_lines=True)
        ).create_stock_picking()

    def _create_stock_moves(self, picking_id):
        if self.env.context.get("use_shedule_lines", False):
            return self.schedule_line_ids._create_stock_moves(picking_id)
        else:
            return super(CreateManualStockPickingWizard, self)._create_stock_moves(
                picking_id
            )


class CreateManualStockPickingWizardLine(models.TransientModel):
    _name = "create.stock.picking.wizard.schedule.line"
    _description = "Create Manual Stock Picking Wizard Line"
    _order = "date_planned, product_id"

    wizard_id = fields.Many2one(
        string="Wizard",
        comodel_name="create.stock.picking.wizard",
        required=True,
        ondelete="cascade",
    )
    schedule_line_id = fields.Many2one("purchase.order.line.schedule")
    purchase_order_line_id = fields.Many2one(
        comodel_name="purchase.order.line", related="schedule_line_id.order_line_id"
    )
    name = fields.Text(string="Description", readonly=True)
    product_id = fields.Many2one(
        "product.product", related="purchase_order_line_id.product_id", string="Product"
    )
    product_uom = fields.Many2one(
        "uom.uom",
        related="purchase_order_line_id.product_uom",
        string="Unit of Measure",
    )
    date_planned = fields.Datetime(related="schedule_line_id.date_planned")
    product_qty = fields.Float(
        string="Quantity",
        related="schedule_line_id.product_qty",
        digits="Product Unit of Measure",
    )
    qty_in_receipt = fields.Float(related="schedule_line_id.qty_in_receipt")
    qty_received = fields.Float(related="schedule_line_id.qty_received")
    remaining_qty = fields.Float(
        string="Remaining Quantity",
        compute="_compute_remaining_qty",
        readonly=True,
        digits="Product Unit of Measure",
    )
    qty = fields.Float(
        string="Receive",
        digits="Product Unit of Measure",
        help="This is the quantity taken into account to create the picking",
    )
    price_unit = fields.Float(
        related="purchase_order_line_id.price_unit", readonly=True
    )
    currency_id = fields.Many2one(
        "res.currency", related="purchase_order_line_id.currency_id"
    )
    partner_id = fields.Many2one(
        "res.partner", related="purchase_order_line_id.partner_id", string="Vendor",
    )
    taxes_id = fields.Many2many(
        "account.tax", related="purchase_order_line_id.taxes_id"
    )

    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = (
                line.product_qty - line.qty_in_receipt - line.qty_received
            )

    def _prepare_stock_moves(self, picking):
        po_line = self.purchase_order_line_id
        return po_line._prepare_stock_moves(picking)

    def _create_stock_moves(self, picking):
        values = []
        for line in self:
            for val in line.with_context(
                schedule_line_id=line.schedule_line_id.id
            )._prepare_stock_moves(picking):
                if val.get("product_uom_qty", False):
                    val["product_uom_qty"] = line.product_uom._compute_quantity(
                        line.qty, line.product_uom, rounding_method="HALF-UP"
                    )
                if (
                    val.get("location_dest_id", False)
                    and not line.wizard_id.picking_id
                    and line.wizard_id.location_dest_id
                ):
                    val["location_dest_id"] = line.wizard_id.location_dest_id.id
                values.append(val)
        return self.env["stock.move"].create(values)
