# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequisitionCreateAlternative(models.TransientModel):
    _inherit = "purchase.requisition.create.alternative"

    partner_id = fields.Many2one(compute="_compute_partner_id", readonly=False)
    partner_ids = fields.Many2many(
        string="Partners", comodel_name="res.partner", required=True
    )

    @api.depends("partner_ids")
    def _compute_partner_id(self):
        for wizard in self:
            partner_id = False
            if wizard.partner_ids:
                partner_id = wizard.partner_ids[0].id
            wizard.partner_id = partner_id

    @api.depends("partner_ids")
    def _compute_purchase_warn(self):
        ret_vals = super()._compute_purchase_warn()
        if self.env.user.has_group("purchase.group_warning_purchase"):
            for partner in self.partner_ids - self.partner_id:
                if partner.purchase_warn == "no-message":
                    partner = partner.parent_id
                if partner and partner.purchase_warn != "no-message":
                    self.purchase_warn_msg = _(
                        "Warning for %(partner)s:\n%(warning_message)s\n",
                        partner=partner.name,
                        warning_message=partner.purchase_warn_msg,
                    )
                    if partner.purchase_warn == "block":
                        self.creation_blocked = True
                        self.purchase_warn_msg += _("This is a blocking warning!\n")
        return ret_vals

    def _get_alternative_values_multiple_vendors(self):
        self.ensure_one()
        vals = self._get_alternative_values()
        all_vendor_vals = [vals]
        for partner in self.partner_ids - self.partner_id:
            partner_vals = vals.copy()
            partner_vals["partner_id"] = partner.id
            all_vendor_vals.append(partner_vals)
        return all_vendor_vals

    def create_alternative_multiple_vendors(self):
        if (
            self.env.user.has_group("purchase.group_warning_purchase")
            and self.creation_blocked
        ):
            raise UserError(
                _(
                    "The vendor you have selected or at least one of the products "
                    "you are copying from the original order has a blocking warning"
                    " on it and cannot be selected to create an alternative."
                )
            )
        vals = self._get_alternative_values_multiple_vendors()
        alt_pos = (
            self.env["purchase.order"]
            .with_context(
                origin_po_id=self.origin_po_id.id, default_requisition_id=False
            )
            .create(vals)
        )
        alt_pos.order_line._compute_tax_id()
        return {
            "name": _("Purchase Order Alternatives"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "purchase.order",
            "domain": [("id", "in", alt_pos.ids)],
        }

    def action_create_alternative(self):
        if len(self.partner_ids) == 1:
            return super().action_create_alternative()
        else:
            return self.create_alternative_multiple_vendors()
