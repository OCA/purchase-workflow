# Copyright 2018-2019 ForgeFlow, S.L.
# Copyright 2024 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("in_progress", "In progress"),
    ("done", "Done"),
    ("rejected", "Rejected"),
]


class PurchaseRequest(models.Model):

    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.request")

    @api.model
    def _default_picking_type(self):
        type_obj = self.env["stock.picking.type"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        types = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "incoming"), ("warehouse_id", "=", False)]
            )
        return types[:1]

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in (
                "to_approve",
                "approved",
                "rejected",
                "in_progress",
                "done",
            ):
                rec.is_editable = False
            else:
                rec.is_editable = True

    name = fields.Char(
        string="Request Reference",
        required=True,
        default=lambda self: _("New"),
        tracking=True,
    )
    is_name_editable = fields.Boolean(
        default=lambda self: self.env.user.has_group("base.group_no_one"),
    )
    origin = fields.Char(string="Source Document")
    date_start = fields.Date(
        string="Creation date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        tracking=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        required=True,
        copy=False,
        tracking=True,
        default=_get_default_requested_by,
        index=True,
    )
    approver_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Approver user",
        default=lambda self: self.env.company.purchase_request_approver_user_id.id,
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref("purchase_request.group_purchase_request_user").id,
            )
        ],
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Approver",
        tracking=True,
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref("purchase_request.group_purchase_request_manager").id,
            )
        ],
        index=True,
    )
    description = fields.Text()
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=False,
        default=_company_get,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=True,
        copy=True,
        tracking=True,
        states={"draft": [("readonly", False)]},
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="line_ids.product_id",
        string="Product",
        readonly=True,
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )
    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")
    is_approvable = fields.Boolean(compute="_compute_is_approvable")
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Picking Type",
        required=True,
        default=_default_picking_type,
    )
    group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Procurement Group",
        copy=False,
        index=True,
    )
    line_count = fields.Integer(
        string="Purchase Request Line count",
        compute="_compute_line_count",
        readonly=True,
    )
    move_count = fields.Integer(
        string="Stock Move count", compute="_compute_move_count", readonly=True
    )
    purchase_count = fields.Integer(
        string="Purchases count", compute="_compute_purchase_count", readonly=True
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    estimated_cost = fields.Monetary(
        compute="_compute_estimated_cost",
        string="Total Estimated Cost",
        store=True,
    )

    @api.depends("approver_user_id")
    def _compute_is_approvable(self):
        user = self.env.user
        user_request_manager = user.has_group(
            "purchase_request.group_purchase_request_manager"
        )
        approvable_states = ["to_approve", "done"]
        for item in self:
            item.is_approvable = item.state in approvable_states and (
                user_request_manager or item.approver_user_id == user
            )

    @api.depends("line_ids", "line_ids.estimated_cost")
    def _compute_estimated_cost(self):
        for rec in self:
            rec.estimated_cost = sum(rec.line_ids.mapped("estimated_cost"))

    @api.depends("line_ids")
    def _compute_purchase_count(self):
        for rec in self:
            rec.purchase_count = len(rec.mapped("line_ids.purchase_lines.order_id"))

    def action_view_purchase_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        lines = self.mapped("line_ids.purchase_lines.order_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_move_count(self):
        for rec in self:
            rec.move_count = len(
                rec.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
            )

    def action_view_stock_picking(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        # remove default filters
        action["context"] = {}
        lines = self.mapped(
            "line_ids.purchase_request_allocation_ids.stock_move_id.picking_id"
        )
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("line_ids"))

    def action_view_purchase_request_line(self):
        action = (
            self.env.ref("purchase_request.purchase_request_line_form_action")
            .sudo()
            .read()[0]
        )
        lines = self.mapped("line_ids")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase_request.purchase_request_line_form").id, "form")
            ]
            action["res_id"] = lines.ids[0]
        return action

    @api.depends("state", "line_ids.product_qty", "line_ids.cancelled")
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = rec.state == "draft" and any(
                not line.cancelled and line.product_qty for line in rec.line_ids
            )

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"state": "draft", "name": self._get_default_name()})
        return super().copy(default)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self._get_default_name()
        requests = super().create(vals_list)
        for vals, request in zip(vals_list, requests):
            if vals.get("assigned_to"):
                request._message_subscribe_assigned_to()
            if vals.get("approver_user_id"):
                request._message_subscribe_approver_user()
        return requests

    def write(self, vals):
        res = super().write(vals)
        for request in self:
            if vals.get("assigned_to"):
                request._message_subscribe_assigned_to()
            if vals.get("approver_user_id"):
                request._message_subscribe_approver_user()
        return res

    def _message_subscribe_assigned_to(self):
        self.ensure_one()
        user = self.assigned_to or self.env.user
        self.message_subscribe(partner_ids=[user.partner_id.id])

    def _message_subscribe_approver_user(self):
        """Subscribe the approver user so that he can view the corresponding request
        (even if he is a user without Manager permissions).
        """
        self.ensure_one()
        if self.approver_user_id:
            self.message_subscribe(partner_ids=[self.approver_user_id.partner_id.id])

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super(PurchaseRequest, self).unlink()

    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        return self.write({"state": "draft"})

    def button_to_approve(self):
        self.to_approve_allowed_check()
        return self.write({"state": "to_approve"})

    def button_approved(self):
        if not self.is_approvable:
            raise UserError(_("You are not allowed to approve this request."))
        return self.sudo().write({"state": "approved"})

    def button_rejected(self):
        if not self.is_approvable:
            raise UserError(_("You are not allowed to reject this request."))
        self.mapped("line_ids").sudo().do_cancel()
        return self.sudo().write({"state": "rejected"})

    def button_in_progress(self):
        return self.write({"state": "in_progress"})

    def button_done(self):
        return self.write({"state": "done"})

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({"state": "rejected"})

    def to_approve_allowed_check(self):
        for rec in self:
            if not rec.to_approve_allowed:
                raise UserError(
                    _(
                        "You can't request an approval for a purchase request "
                        "which is empty. (%s)"
                    )
                    % rec.name
                )
