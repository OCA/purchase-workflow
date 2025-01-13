# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    service_picking_count = fields.Integer(
        compute="_compute_service_picking",
        string="Service Picking count",
        default=0,
        store=True,
    )
    service_picking_ids = fields.Many2many(
        comodel_name="service.picking",
        compute="_compute_service_picking",
        string="Service Receptions",
        copy=False,
        store=True,
    )
    is_service_shipped = fields.Boolean(compute="_compute_is_service_shipped")

    @api.depends("order_line.service_picking_line_ids.picking_id")
    def _compute_service_picking(self):
        for order in self:
            pickings = order.order_line.mapped("service_picking_line_ids.picking_id")
            order.service_picking_ids = pickings
            order.service_picking_count = len(pickings)

    @api.depends("service_picking_ids", "service_picking_ids.state")
    def _compute_is_service_shipped(self):
        for order in self:
            if order.service_picking_ids and all(
                x.state in ["done", "cancel"] for x in order.service_picking_ids
            ):
                order.is_service_shipped = True
            else:
                order.is_service_shipped = False

    def _prepare_service_picking_vals(self):
        return {
            "partner_id": self.partner_id.id,
            "user_id": False,
            "date": self.date_order,
            "origin": self.name,
            "company_id": self.company_id.id,
            "purchase_id": self.id,
            "state": "in_progress",
        }

    def _create_service_picking(self):
        sp_model = self.env["service.picking"]
        for order in self.filtered(lambda x: x.state in ("purchase", "done")):
            if any(p.type == "service" for p in order.order_line.product_id):
                order = order.with_company(order.company_id)
                service_pickings = order.service_picking_ids.filtered(
                    lambda x: x.state not in ("done", "cancel")
                )
                if not service_pickings:
                    picking = sp_model.with_user(SUPERUSER_ID).create(
                        order._prepare_service_picking_vals()
                    )
                else:
                    picking = service_pickings[0]
                picking_lines = order.order_line._create_service_picking_lines(picking)
                seq = 0
                for picking_line in sorted(picking_lines, key=lambda pl: pl.date):
                    seq += 5
                    picking_line.sequence = seq
                picking.message_post_with_view(
                    "mail.message_origin_link",
                    values={"self": picking, "origin": order},
                    subtype_id=self.env.ref("mail.mt_note").id,
                )
        return True

    def button_approve(self, force=False):
        result = super().button_approve(force=force)
        self._create_service_picking()
        return result

    def button_cancel(self):
        for order in self:
            if any(pick.state == "done" for pick in order.service_picking_ids):
                raise UserError(
                    _(
                        "Unable to cancel purchase order %s as some service pickings "
                        "have already been done."
                    )
                    % (order.name)
                )
            for pick in order.service_picking_ids.filtered(
                lambda x: x.state != "cancel"
            ):
                pick.action_cancel()

        return super().button_cancel()

    def action_view_service_picking(self):
        result = self.env["ir.actions.actions"]._for_xml_id(
            "purchase_service_picking.action_service_picking_tree_all"
        )
        result["context"] = {
            "default_partner_id": self.partner_id.id,
            "default_origin": self.name,
            "default_purchcase_id": self.id,
        }
        pick_ids = self.mapped("service_picking_ids")
        # choose the view_mode accordingly
        if not pick_ids or len(pick_ids) > 1:
            result["domain"] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref(
                "view_service_picking_form.view_service_picking_form", False
            )
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [
                    (state, view) for state, view in result["views"] if view != "form"
                ]
            else:
                result["views"] = form_view
            result["res_id"] = pick_ids.id
        return result


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    service_picking_line_ids = fields.One2many(
        comodel_name="service.picking.line",
        inverse_name="purchase_line_id",
        string="Service picking lines",
        readonly=True,
        copy=False,
    )

    @api.depends(
        "service_picking_line_ids.state",
        "service_picking_line_ids.product_uom_qty",
        "service_picking_line_ids.product_uom_id",
    )
    def _compute_qty_received(self):
        custom_lines = self.filtered(
            lambda x: x.product_id.type == "service"
            and x.product_id.purchase_method == "receive"
        )
        res = super(PurchaseOrderLine, self - custom_lines)._compute_qty_received()
        for line in custom_lines:
            total = 0
            for spl in line.service_picking_line_ids.filtered(
                lambda x: x.state == "done"
            ):
                spl_qty = spl.product_uom_id._compute_quantity(
                    spl.quantity_done, line.product_uom, rounding_method="HALF-UP"
                )
                if spl.origin_returned_line_id:
                    total -= spl_qty
                else:
                    total += spl_qty
            line._track_qty_received(total)
            line.qty_received = total
        return res

    def _get_outgoing_incoming_service_picking_lines(self):
        lines = self.service_picking_line_ids.filtered(lambda x: x.state != "cancel")
        outgoing_lines = lines.filtered(lambda x: x.origin_returned_line_id)
        incoming_lines = lines - outgoing_lines
        return outgoing_lines, incoming_lines

    def _prepare_service_picking_line_vals(self, picking, qty):
        self.ensure_one()
        date_planned = self.date_planned or self.order_id.date_planned
        return {
            "name": (self.product_id.display_name or "")[:2000],
            "product_id": self.product_id.id,
            "description_picking": self.name,
            "date": date_planned,
            "picking_id": picking.id,
            "purchase_line_id": self.id,
            "product_uom_qty": qty,
            "product_uom_id": self.product_uom.id,
            "sequence": self.sequence,
        }

    def _prepare_service_picking_lines(self, picking):
        self.ensure_one()
        res = []
        uom = self.product_uom
        qty_to_attach = 0
        qty = 0.0
        out_lines, in_lines = self._get_outgoing_incoming_service_picking_lines()
        for line in out_lines:
            qty -= line.product_uom_id._compute_quantity(
                line.product_uom_qty, uom, rounding_method="HALF-UP"
            )
        for line in in_lines:
            qty += line.product_uom_id._compute_quantity(
                line.product_uom_qty, uom, rounding_method="HALF-UP"
            )
        qty_to_push = self.product_uom_qty - qty
        if float_compare(qty_to_attach, 0.0, precision_rounding=uom.rounding) > 0:
            product_uom_qty = uom._compute_quantity(
                qty_to_attach, uom, rounding_method="HALF-UP"
            )
            res.append(
                self._prepare_service_picking_line_vals(picking, product_uom_qty)
            )
        if not float_is_zero(qty_to_push, precision_rounding=uom.rounding):
            product_uom_qty = uom._compute_quantity(
                qty_to_push, uom, rounding_method="HALF-UP"
            )
            res.append(
                self._prepare_service_picking_line_vals(picking, product_uom_qty)
            )
        return res

    def _create_service_picking_lines(self, picking):
        values = []
        for line in self.filtered(lambda x: x.product_id.type == "service"):
            for val in line._prepare_service_picking_lines(picking):
                values.append(val)
        return self.env["service.picking.line"].create(values)

    def _create_or_update_sevice_picking(self):
        for pol in self.filtered(lambda x: x.product_id.type == "service"):
            # Prevent decreasing below received quantity
            if (
                float_compare(
                    pol.product_qty, pol.qty_received, pol.product_uom.rounding
                )
                < 0
            ):
                raise UserError(
                    _(
                        "You cannot decrease the ordered quantity below the received "
                        "quantity.\nCreate a return first."
                    )
                )
            # If the user increased quantity of existing line or created a new line
            pickings = pol.order_id.service_picking_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            )
            picking = pickings and pickings[0] or False
            if not picking:
                picking = self.env["service.picking"].create(
                    pol.order_id._prepare_service_picking_vals()
                )
                pol._create_service_picking_lines(picking)
            else:
                self.env["service.picking.line"].create(
                    pol._prepare_service_picking_lines(picking)
                )
            picking.line_ids._merge_lines()
            precision_digits = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            if all(
                float_is_zero(line.product_uom_qty, precision_digits=precision_digits)
                for line in picking.line_ids
            ):
                picking.action_cancel()

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.filtered(
            lambda x: x.order_id.state == "purchase" and x.product_id.type == "service"
        )._create_or_update_sevice_picking()
        return lines

    def write(self, values):
        lines = self.filtered(
            lambda x: x.order_id.state == "purchase" and x.product_id.type == "service"
        )
        previous_product_qty = {line.id: line.product_qty for line in lines}
        result = super().write(values)
        if "product_qty" in values:
            lines = lines.filtered(
                lambda x: float_compare(
                    previous_product_qty[x.id],
                    x.product_qty,
                    precision_rounding=x.product_uom.rounding,
                )
                != 0
            )
            lines._create_or_update_sevice_picking()
        return result
