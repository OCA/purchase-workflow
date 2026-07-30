# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    override_supplier_approval = fields.Boolean(
        copy=False,
        help="Check this to override supplier approval validation",
    )
    override_reason = fields.Text(
        copy=False,
        help="Reason for overriding supplier approval validation",
    )
    has_unapproved_supplier = fields.Boolean(
        compute="_compute_has_unapproved_supplier",
        help="Technical field to track if PO has unapproved suppliers",
    )
    can_manage_approved_suppliers = fields.Boolean(
        compute="_compute_can_manage_approved_suppliers",
        help="Technical field to check if current user can manage approved suppliers",
    )

    @api.depends("order_line.has_unapproved_supplier")
    def _compute_has_unapproved_supplier(self):
        for order in self:
            order.has_unapproved_supplier = any(
                line.has_unapproved_supplier for line in order.order_line
            )

    def _compute_can_manage_approved_suppliers(self):
        group_name = "purchase_supplier_approved.group_manage_approved_suppliers"
        can_manage_approved_suppliers = self.env.user.has_group(group_name)
        for order in self:
            order.can_manage_approved_suppliers = can_manage_approved_suppliers

    @api.constrains("override_supplier_approval", "override_reason")
    def _check_override_reason(self):
        for order in self:
            if order.override_supplier_approval and not order.override_reason:
                raise ValidationError(
                    _("Override reason is required when overriding supplier approval.")
                )

    def write(self, vals):
        # Additional security check for override fields
        if vals.get("override_supplier_approval") or vals.get("override_reason"):
            group_name = "purchase_supplier_approved.group_manage_approved_suppliers"
            if not self.env.user.has_group(group_name):
                raise ValidationError(
                    _(
                        "Only users with 'Manage Approved Suppliers' permission "
                        "can modify override settings."
                    )
                )
        return super().write(vals)

    def button_confirm(self):
        """Override to add supplier approval validation"""
        for order in self:
            if order.has_unapproved_supplier and not order.override_supplier_approval:
                unapproved_products = order.order_line.filtered(
                    lambda line: line.has_unapproved_supplier
                ).product_id
                raise UserError(
                    _(
                        "Cannot confirm purchase order. "
                        "The following products are not approved "
                        "for supplier %(supplier)s:\n\n%(products)s\n\n"
                        "Please contact an administrator to approve these suppliers "
                        "or use the override option "
                        "if you have the required permissions."
                    )
                    % {
                        "supplier": order.partner_id.name,
                        "products": "\n".join(
                            f"• {product.display_name}"
                            for product in unapproved_products
                        ),
                    }
                )

        return super().button_confirm()

    @api.onchange("partner_id", "order_line")
    def _onchange_check_supplier_approval(self):
        """Show warning when adding unapproved suppliers"""
        if not self.partner_id:
            return

        unapproved_products = self.order_line.filtered(
            lambda line: line.has_unapproved_supplier
        ).product_id
        if unapproved_products:
            return {
                "warning": {
                    "title": _("Unapproved Supplier Warning"),
                    "message": _(
                        "The supplier %(supplier)s is not approved "
                        "for the following products:\n\n%(products)s\n\n"
                    )
                    % {
                        "supplier": self.partner_id.name,
                        "products": "\n".join(
                            f"• {product.display_name}"
                            for product in unapproved_products
                        ),
                    },
                }
            }


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    has_unapproved_supplier = fields.Boolean(
        compute="_compute_has_unapproved_supplier",
        help="Technical field to track if this line has an unapproved supplier",
    )

    @api.depends("product_id", "order_id.partner_id", "order_id.date_order")
    def _compute_has_unapproved_supplier(self):
        for line in self:
            if not line.product_id or not line.order_id.partner_id:
                line.has_unapproved_supplier = False
                continue

            product_tmpl = line.product_id.product_tmpl_id
            if not product_tmpl.is_approved_supplier_required:
                line.has_unapproved_supplier = False
                continue

            # Check if supplier is approved for this product
            current_date = (
                line.order_id.date_order
                if line.order_id.date_order
                else fields.Date.context_today(line)
            )
            is_approved = product_tmpl.is_supplier_approved(
                line.order_id.partner_id.id, current_date
            )
            line.has_unapproved_supplier = not is_approved

    @api.onchange("product_id")
    def onchange_product_id(self):
        """Check supplier approval when changing product"""
        result = super().onchange_product_id()

        # Trigger the compute of has_unapproved_supplier
        self._compute_has_unapproved_supplier()

        if self.has_unapproved_supplier:
            warning = {
                "title": _("Unapproved Supplier Warning"),
                "message": _(
                    "The supplier %(supplier)s "
                    "is not approved for product %(product)s. "
                )
                % {
                    "supplier": self.order_id.partner_id.name,
                    "product": self.product_id.display_name,
                },
            }

            if result:
                result["warning"] = warning
            else:
                result = {"warning": warning}

        return result
