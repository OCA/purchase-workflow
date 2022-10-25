# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_general_discount_field = fields.Selection(
        selection="_get_purchase_discount_fields",
        string="Purchase Discount Field",
        default="discount",
        help="Set the purchase line discount field in which the "
        "discounts will be applied.",
    )

    @api.model
    def _get_purchase_discount_fields(self):
        """Extensible method to add possible discounts. We offer in advance
        the posibility of using purchase_triple_discount so no bridge
        module is needed"""
        discount_fields = [("discount", _("Discount"))]
        purchase_line_fields = self.env["purchase.order.line"]._fields.keys()
        if "discount2" in purchase_line_fields:
            discount_fields += [
                ("discount2", _("Discount 2")),
            ]
        if "discount3" in purchase_line_fields:
            discount_fields += [
                ("discount3", _("Discount 3")),
            ]
        return discount_fields
