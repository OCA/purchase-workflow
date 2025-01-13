# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from itertools import groupby
from operator import itemgetter

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class ServicePicking(models.Model):
    _name = "service.picking"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Service Picking"
    _order = "scheduled_date asc, id desc"

    name = fields.Char(
        string="Reference", default="/", copy=False, index=True, readonly=True
    )
    origin = fields.Char(
        string="Source Document",
        index=True,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
        help="Reference of the document",
    )
    backorder_id = fields.Many2one(
        comodel_name="service.picking",
        string="Back Order of",
        copy=False,
        index=True,
        readonly=True,
        check_company=True,
    )
    backorder_ids = fields.One2many(
        comodel_name="service.picking",
        inverse_name="backorder_id",
        string="Back Orders",
    )
    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase Order",
        ondelete="cascade",
        index=True,
        copy=False,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        copy=False,
        index=True,
        readonly=True,
        tracking=True,
    )
    scheduled_date = fields.Datetime(
        string="Scheduled Date",
        compute="_compute_scheduled_date",
        inverse="_inverse_scheduled_date",
        store=True,
        index=True,
        default=fields.Datetime.now,
        tracking=True,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )
    date_deadline = fields.Datetime(
        string="Deadline",
        compute="_compute_date_deadline",
        store=True,
        help="Date Promise to the customer on the top level document (SO/PO)",
    )
    date = fields.Datetime(
        string="Creation Date",
        default=fields.Datetime.now,
        index=True,
        tracking=True,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
        help="Creation Date, usually the time of the order",
    )
    date_done = fields.Datetime(
        string="Date of Transfer",
        copy=False,
        readonly=True,
        help="Date at which the transfer has been processed or cancelled.",
    )
    line_ids = fields.One2many(
        comodel_name="service.picking.line",
        inverse_name="picking_id",
        string="Lines",
        copy=False,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Contact",
        check_company=True,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company.id,
        readonly=True,
        states={"draft": [("readonly", False)], "reserved": [("readonly", False)]},
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        tracking=True,
        domain=lambda self: [
            ("groups_id", "in", self.env.ref("purchase.group_purchase_user").id)
        ],
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
        default=lambda self: self.env.user,
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name, company_id)",
            "Reference must be unique per company!",
        ),
    ]

    @api.depends("line_ids.state", "line_ids.date")
    def _compute_scheduled_date(self):
        for picking in self:
            lines_dates = picking.line_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            ).mapped("date")
            picking.scheduled_date = min(
                lines_dates, default=picking.scheduled_date or fields.Datetime.now()
            )

    @api.depends("line_ids.date_deadline")
    def _compute_date_deadline(self):
        for picking in self:
            picking.date_deadline = min(
                picking.line_ids.filtered("date_deadline").mapped("date_deadline"),
                default=False,
            )

    def _inverse_scheduled_date(self):
        for picking in self:
            if picking.state in ("done", "cancel"):
                raise UserError(
                    _(
                        "You cannot change the Scheduled Date on a done or cancelled transfer."
                    )
                )
            picking.line_ids.write({"date": picking.scheduled_date})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "service.picking"
                ) or _("New")
        return super().create(vals_list)

    def action_confirm(self):
        for item in self.filtered(lambda x: x.state == "draft"):
            item.state = "in_progress"

    def _check_immediate(self):
        immediate_pickings = self.browse()
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for picking in self.filtered(lambda x: x.state == "in_progress"):
            if all(
                float_is_zero(line.quantity_done, precision_digits=precision_digits)
                for line in picking.line_ids
            ):
                immediate_pickings |= picking
        return immediate_pickings

    def _check_backorder(self):
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        backorder_pickings = self.browse()
        for picking in self:
            qty_todo = {}
            qty_done = {}
            for line in picking.mapped("line_ids").filtered(
                lambda x: x.state != "cancel"
            ):
                product = line.product_id
                qty_todo.setdefault(product.id, 0)
                qty_done.setdefault(product.id, 0)
                qty_todo_line = line.product_uom_id._compute_quantity(
                    line.product_uom_qty, product.uom_id, rounding_method="HALF-UP"
                )
                qty_todo[product.id] += qty_todo_line
                qty_done_line = line.product_uom_id._compute_quantity(
                    line.quantity_done,
                    product.uom_id,
                    rounding_method="HALF-UP",
                )
                qty_done[product.id] += qty_done_line
            if any(
                float_compare(
                    qty_done[x],
                    qty_todo.get(x, 0),
                    precision_digits=prec,
                )
                == -1
                for x in qty_done
            ):
                backorder_pickings |= picking
        return backorder_pickings

    def _prepare_split_vals(self):
        return {
            "backorder_id": self.id,
            "partner_id": self.partner_id.id,
            "user_id": self.user_id.id,
            "date": self.date,
            "origin": self.origin,
            "company_id": self.company_id.id,
            "purchase_id": self.purchase_id.id,
            "state": "in_progress",
        }

    def _create_backorder(self):
        sp_model = self.env["service.picking"]
        backorder = sp_model
        backorder_line_vals = []
        rounding = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for line in self.line_ids:
            if (
                float_compare(
                    line.quantity_done, line.product_uom_qty, precision_digits=rounding
                )
                < 0
            ):
                qty_split = line.product_uom_id._compute_quantity(
                    line.product_uom_qty - line.quantity_done,
                    line.product_id.uom_id,
                    rounding_method="HALF-UP",
                )
                if not backorder:
                    backorder = sp_model.with_user(SUPERUSER_ID).create(
                        self._prepare_split_vals()
                    )
                    self.message_post(
                        body=_(
                            "The backorder <a href=# data-oe-model=service.picking"
                            " data-oe-id=%d>%s</a> has been created."
                        )
                        % (backorder.id, backorder.name)
                    )
                backorder_line_vals.append(
                    line._prepare_line_split_vals(backorder, qty_split)
                )
        if backorder_line_vals:
            self.env["service.picking.line"].create(backorder_line_vals)

    def action_validate(self):
        self = self.filtered(lambda x: x.state == "in_progress")
        if not self.env.context.get("action_validate_picking_ids"):
            self = self.with_context(action_validate_picking_ids=self.ids)
        pickings_not_to_backorder = self.env["service.picking"]
        if self.env.context.get("picking_ids_not_to_backorder"):
            pickings_not_to_backorder = self.browse(
                self.env.context["picking_ids_not_to_backorder"]
            )
        for item in self:
            # Inmediate wizard
            if not self.env.context.get("skip_immediate"):
                pickings_to_immediate = self._check_immediate()
                if pickings_to_immediate:
                    return pickings_to_immediate._action_generate_immediate_wizard()
            # Backorder wizard
            if not self.env.context.get("skip_backorder"):
                pickings_to_backorder = self._check_backorder()
                if pickings_to_backorder:
                    return pickings_to_backorder._action_generate_backorder_wizard()
            # Backorder process
            if item not in pickings_not_to_backorder:
                item._create_backorder()
            item._action_done()

    def _action_done(self):
        """This method may be useful in other modules (e.g. analytic)."""
        items = self.filtered(lambda x: x.state == "in_progress")
        items.line_ids._action_done()
        items.write({"state": "done", "date_done": fields.Datetime.now()})

    def action_cancel(self):
        for item in self.filtered(lambda x: x.state == "in_progress"):
            item.state = "cancel"

    def _action_generate_immediate_wizard(self):
        view = self.env.ref("purchase_service_picking.view_immediate_transfer")
        return {
            "name": _("Immediate Transfer?"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "service.immediate.transfer",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": dict(
                self.env.context, default_picking_ids=[(4, p.id) for p in self]
            ),
        }

    def _action_generate_backorder_wizard(self):
        view = self.env.ref("purchase_service_picking.view_backorder_confirmation")
        return {
            "name": _("Create Backorder?"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "service.backorder.confirmation",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": dict(
                self.env.context, default_picking_ids=[(4, p.id) for p in self]
            ),
        }


class ServicePickingLine(models.Model):
    _name = "service.picking.line"
    _description = "Service Picking Line"
    _order = "picking_id, sequence, id"

    picking_id = fields.Many2one(
        comodel_name="service.picking",
        string="Picking",
        index=True,
        required=True,
        ondelete="cascade",
    )
    description_picking = fields.Text(string="Description of Picking")
    sequence = fields.Integer(string="Sequence", default=10)
    company_id = fields.Many2one(related="picking_id.company_id")
    purchase_line_id = fields.Many2one(comodel_name="purchase.order.line")
    state = fields.Selection(related="picking_id.state")
    name = fields.Char(string="Description", required=True)
    origin_returned_line_id = fields.Many2one(
        comodel_name="service.picking.line",
        string="Origin return line",
        copy=False,
        index=True,
        help="Line that created the return line",
    )
    returned_line_ids = fields.One2many(
        comodel_name="service.picking.line",
        inverse_name="origin_returned_line_id",
        string="All returned lines",
    )
    date = fields.Datetime(
        string="Date Scheduled",
        default=fields.Datetime.now,
        index=True,
        required=True,
    )
    date_deadline = fields.Datetime(
        string="Deadline",
        readonly=True,
        help="Date Promise to the customer on the top level document (SO/PO)",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        check_company=True,
        domain="[('type', '=', 'service')]",
        index=True,
        required=True,
        states={"done": [("readonly", True)]},
    )
    product_uom_qty = fields.Float(
        string="Demand",
        digits="Product Unit of Measure",
        default=0.0,
        required=True,
        states={"done": [("readonly", True)]},
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom", string="Unit of Measure", required=True
    )
    quantity_done = fields.Float(
        string="Quantity Done", digits="Product Unit of Measure", copy=False
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.name = (self.product_id.display_name or "")[:2000]
        self.product_uom_id = self.product_id.uom_po_id or self.product_id.uom_id

    def _prepare_line_split_vals(self, picking, qty):
        return {
            "picking_id": picking.id,
            "purchase_line_id": self.purchase_line_id.id,
            "name": self.name,
            "date_deadline": self.date_deadline,
            "product_id": self.product_id.id,
            "product_uom_qty": qty,
            "product_uom_id": self.product_uom_id.id,
        }

    @api.model
    def _prepare_merge_lines_distinct_fields(self):
        return ["purchase_line_id", "product_id", "product_uom_id"]

    @api.model
    def _prepare_merge_line_sort_method(self, line):
        line.ensure_one()
        return [line.purchase_line_id.id, line.product_id.id, line.product_uom_id.id]

    def _merge_lines_fields(self):
        return {
            "product_uom_qty": sum(self.mapped("product_uom_qty")),
        }

    def _merge_lines(self):
        spl_model = self.env["service.picking.line"]
        distinct_fields = self._prepare_merge_lines_distinct_fields()
        lines_to_unlink = spl_model
        lines_to_merge = []
        for _k, g in groupby(
            sorted(self, key=self._prepare_merge_line_sort_method),
            key=itemgetter(*distinct_fields),
        ):
            lines = spl_model.concat(*g).filtered(lambda x: x.state == "in_progress")
            if len(lines) > 1:
                lines_to_merge.append(lines)

        for lines in lines_to_merge:
            lines[0].write(lines._merge_lines_fields())
            lines_to_unlink |= lines[1:]

        if lines_to_unlink:
            lines_to_unlink.sudo().unlink()
        return (self | spl_model.concat(*lines_to_merge)) - lines_to_unlink

    def _action_done(self):
        """This method may be useful in other modules (e.g. analytic)."""
        for line in self:
            line.write(
                {"date": fields.Datetime.now(), "product_uom_qty": line.quantity_done}
            )
