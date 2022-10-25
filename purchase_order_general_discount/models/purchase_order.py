# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    general_discount = fields.Float(
        digits="Discount",
        string="Gen. Disc. (%)",
    )

    _sql_constraints = [
        (
            "general_discount_limit",
            "CHECK (general_discount <= 100.0)",
            "Discount must be lower than 100%.",
        ),
    ]

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        super().onchange_partner_id()
        self.general_discount = (
            self.partner_id.commercial_partner_id.purchase_general_discount
        )

    def _get_general_discount_field(self):
        """We can set in settings another discount field to be applied
        For example, if we had purchase_triple_dicount, we could set the
        general discount in discount3 to be applied after all other
        discounts"""
        discount_field = self.company_id.purchase_general_discount_field
        return discount_field or "discount"

    @api.onchange("general_discount")
    def onchange_general_discount(self):
        discount_field = self._get_general_discount_field()
        self.mapped("order_line").update({discount_field: self.general_discount})

    def action_update_general_discount(self):
        for order in self:
            order.onchange_general_discount()

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """The purpose of this is to write a context on "order_line" field
        respecting other contexts on this field.
        There is a PR (https://github.com/odoo/odoo/pull/26607) to odoo for
        avoiding this. If merged, remove this method and add the attribute
        in the field.
        """
        res = super().fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == "form":
            discount_field = self._get_general_discount_field()
            order_xml = etree.XML(res["arch"])
            order_line_fields = order_xml.xpath("//field[@name='order_line']")
            if order_line_fields:
                order_line_field = order_line_fields[0]
                context = order_line_field.attrib.get("context", "{}").replace(
                    "{",
                    "{{'default_{}': general_discount, ".format(discount_field),
                    1,
                )
                order_line_field.attrib["context"] = context
                res["arch"] = etree.tostring(order_xml)
        return res
