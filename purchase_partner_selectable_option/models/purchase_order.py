# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id, view_type, **options)

        if view_type == "form":
            purchase_xml = etree.XML(res["arch"])
            partner_fields = purchase_xml.xpath('//field[@name="partner_id"]')

            if partner_fields:
                partner_fields = partner_fields[0]
                domain = partner_fields.get("domain", "[]").replace(
                    "[", "[('purchase_selectable', '=', True),"
                )
                partner_fields.attrib["domain"] = domain
                res["arch"] = etree.tostring(purchase_xml, encoding="unicode")

        return res
