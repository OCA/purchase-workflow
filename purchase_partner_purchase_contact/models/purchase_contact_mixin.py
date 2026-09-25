# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class PurchaseContactMixin(models.AbstractModel):
    """Add a Purchase Contact (a contact person of the vendor)."""

    _name = "purchase.contact.mixin"
    _description = "Purchase Contact Mixin"

    purchase_contact_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Purchase Contact",
        domain=(
            "[('id', 'child_of', partner_id), "
            "('is_company', '=', False), ('id', '!=', partner_id), "
            "('type', '=', 'purchase')]"
        ),
        copy=True,
        help="Contact person for this record. "
        "Only child contacts of the partner can be selected.",
    )

    @api.onchange("partner_id")
    def _onchange_partner_id_purchase_contact_auto_switch(self):
        """If a contact person is picked as partner, move it to the contact."""
        self._purchase_contact_apply_auto_switch()

    def _purchase_contact_apply_auto_switch(self):
        if (
            self.partner_id
            and self.partner_id.commercial_partner_id
            and self.partner_id.commercial_partner_id != self.partner_id
        ):
            contact = self.partner_id
            self.partner_id = contact.commercial_partner_id
            self.purchase_contact_partner_id = contact
            return True
        return False

    @api.onchange("partner_id")
    def _onchange_partner_id_clear_purchase_contact(self):
        """Clear purchase contact when it no longer belongs to the partner."""
        if self.purchase_contact_partner_id:
            if (
                self.purchase_contact_partner_id.commercial_partner_id
                != self.partner_id
                and self.purchase_contact_partner_id != self.partner_id
            ):
                self.purchase_contact_partner_id = False
