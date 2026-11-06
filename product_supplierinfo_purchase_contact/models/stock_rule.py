# Copyright 2024 Tecnativa - Carolina Fernandez
# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_purchase_contact(self, values):
        # The vendor pricelist is a dict of seller info since 20.0
        supplierinfo = (values.get("supplier") or {}).get("supplierinfo")
        return supplierinfo.purchase_partner_id if supplierinfo else False

    def _make_po_get_domain(self, company_id, values, partner):
        # Keep the vendor for the rest of the domain (buyer, currency, RFQ
        # grouping...), as _prepare_purchase_order takes those values from it,
        # and only search by the purchase contact, that is the partner of the RFQ.
        domain = super()._make_po_get_domain(company_id, values, partner)
        purchase_contact = self._get_purchase_contact(values)
        if purchase_contact:
            domain = tuple(
                ("partner_id", "=", purchase_contact.id)
                if leaf[0] == "partner_id"
                else leaf
                for leaf in domain
            )
        return domain

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)
        purchase_contact = self._get_purchase_contact(values[0])
        if purchase_contact:
            res["partner_id"] = purchase_contact.id
        return res
