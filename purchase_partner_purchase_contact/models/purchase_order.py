# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "purchase.contact.mixin"]

    def _mail_get_partners(self, introspect_fields=False):
        """Default the mail recipient to the purchase contact, else the vendor."""
        res = super()._mail_get_partners(introspect_fields=introspect_fields)
        for record in self:
            if res.get(record.id) != record.partner_id:
                continue
            contact = record.purchase_contact_partner_id
            if contact and contact.email:
                res[record.id] = contact
        return res
