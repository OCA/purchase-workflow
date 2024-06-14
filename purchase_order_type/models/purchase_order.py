# Copyright 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    order_type = fields.Many2one(
        comodel_name="purchase.order.type",
        string="Type",
        ondelete="restrict",
        domain="[('company_id', 'in', [False, company_id])]",
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        purchase_type = (
            self.partner_id.purchase_type
            or self.partner_id.commercial_partner_id.purchase_type
        )
        if purchase_type:
            self.order_type = purchase_type
        return res

    @api.onchange("order_type")
    def onchange_order_type(self):
        for order in self:
            if order.order_type.payment_term_id:
                order.payment_term_id = order.order_type.payment_term_id.id
            if order.order_type.incoterm_id:
                order.incoterm_id = order.order_type.incoterm_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get("name", "/") == "/" and values.get("order_type"):
                purchase_type = self.env["purchase.order.type"].browse(
                    values["order_type"]
                )
                if purchase_type.sequence_id:
                    values["name"] = purchase_type.sequence_id.next_by_id(
                        sequence_date=values.get("date_order")
                    )
        return super().create(vals_list)

    @api.constrains("company_id")
    def _check_po_type_company(self):
        if self.filtered(
            lambda r: r.order_type.company_id
            and r.company_id
            and r.order_type.company_id != r.company_id
        ):
            raise ValidationError(_("Document's company and type's company mismatch"))

    def _default_order_type(self):
        return self.env["purchase.order.type"].search(
            [("company_id", "in", [False, self.company_id.id])],
            limit=1,
        )

    @api.onchange("company_id")
    def _onchange_company(self):
        if not self.order_type or (
            self.order_type
            and self.order_type.company_id not in [self.company_id, False]
        ):
            self.order_type = self._default_order_type()
