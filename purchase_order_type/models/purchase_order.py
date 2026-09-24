# Copyright 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    order_type = fields.Many2one(
        comodel_name="purchase.order.type",
        states=Purchase.READONLY_STATES,
        string="Type",
        ondelete="restrict",
        domain="[('company_id', 'in', [False, company_id])]",
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if not self.partner_id:
            self.order_type = False
        else:
            # Overwrite whenever the vendor (or its commercial parent) has
            # a type of its own - matching this method's original
            # behavior. Only fall back to the company default when
            # order_type is still empty: an already-set type is never
            # downgraded to the generic default just because this vendor
            # doesn't have one of its own.
            vendor_type = self._get_vendor_order_type(self.partner_id)
            if vendor_type or not self.order_type:
                self.order_type = vendor_type or self._default_order_type(
                    self.company_id
                )
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
        self._set_order_type_defaults(vals_list)
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

    def _set_order_type_defaults(self, vals_list):
        """Resolve a missing order type, then carry its payment term/incoterm.

        A vals that already names an order type, or whose partner
        provides one of its own, is left as is for the type;
        payment_term_id/incoterm_id are only filled in when the vals
        doesn't already name them either, mirroring what
        onchange_order_type does in the form.
        """
        # Browsing the partners (and, below, the order types) as one batch
        # instead of one by one keeps this at a handful of queries no
        # matter how many vals_list entries are being created at once -
        # the individual records below still share that batch's prefetch.
        partner_ids = {
            values["partner_id"] for values in vals_list if values.get("partner_id")
        }
        partner_by_id = {
            partner.id: partner
            for partner in self.env["res.partner"].browse(partner_ids)
        }

        default_per_company = {}
        for values in vals_list:
            if not values.get("order_type"):
                partner = partner_by_id.get(
                    values.get("partner_id"), self.env["res.partner"]
                )
                vendor_type = self._get_vendor_order_type(partner)
                if vendor_type:
                    values["order_type"] = vendor_type.id
                else:
                    company_id = values.get("company_id") or self.env.company.id
                    if company_id not in default_per_company:
                        company = self.env["res.company"].browse(company_id)
                        default_per_company[company_id] = self._default_order_type(
                            company
                        ).id
                    if default_per_company[company_id]:
                        values["order_type"] = default_per_company[company_id]

        order_type_ids = {
            values["order_type"] for values in vals_list if values.get("order_type")
        }
        order_type_by_id = {
            order_type.id: order_type
            for order_type in self.env["purchase.order.type"].browse(order_type_ids)
        }
        for values in vals_list:
            order_type = order_type_by_id.get(
                values.get("order_type"), self.env["purchase.order.type"]
            )
            if order_type.payment_term_id and not values.get("payment_term_id"):
                values["payment_term_id"] = order_type.payment_term_id.id
            if order_type.incoterm_id and not values.get("incoterm_id"):
                values["incoterm_id"] = order_type.incoterm_id.id

    @api.constrains("company_id")
    def _check_po_type_company(self):
        if self.filtered(
            lambda r: r.order_type.company_id
            and r.company_id
            and r.order_type.company_id != r.company_id
        ):
            raise ValidationError(_("Document's company and type's company mismatch"))

    def _get_order_type(self, partner, company):
        """Return the order type that fits ``partner``, or ``company``'s default."""
        return self._get_vendor_order_type(partner) or self._default_order_type(company)

    def _get_vendor_order_type(self, partner):
        return partner.purchase_type or partner.commercial_partner_id.purchase_type

    def _default_order_type(self, company=None):
        company = company or self.company_id
        po_type = self.env["purchase.order.type"]
        domain = [("is_default", "=", True)]
        # A default configured for this specific company always wins over a
        # global one: the global default exists for companies that have no
        # default of their own, not to override a more specific choice.
        return po_type.search(
            domain + [("company_id", "=", company.id)], limit=1
        ) or po_type.search(domain + [("company_id", "=", False)], limit=1)

    @api.onchange("company_id")
    def _onchange_company(self):
        if not self.order_type or (
            self.order_type
            and self.order_type.company_id not in [self.company_id, False]
        ):
            self.order_type = self._get_order_type(self.partner_id, self.company_id)
