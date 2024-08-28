# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    product_supplied_count = fields.Integer(compute="_compute_product_supplied_count")

    def _compute_product_supplied_count(self):
        data = self.env["product.supplierinfo"].read_group(
            [("partner_id", "in", self.ids)], ["partner_id"], ["partner_id"]
        )
        mapping = {d["partner_id"][0]: d["partner_id_count"] for d in data}
        for item in self:
            item.product_supplied_count = mapping.get(item.id, 0)

    def action_see_products_by_seller(self):
        domain = [("partner_id", "=", self.id)]
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "product.product_supplierinfo_type_action"
        )
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_partner_id": self.id,
                "search_default_partner_id": self.id,
                "visible_product_tmpl_id": False,
            }
        )
        action.update({"domain": domain, "context": ctx})
        return action
