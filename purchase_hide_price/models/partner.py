from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    hide_purchase_price = fields.Boolean(
        string="Hide Prices",
        help="Hide purchase prices for this vendor and for users belong "
        "to 'Purchase hide prices' group.",
        groups="purchase.group_purchase_manager",
    )

    def _hide_purchase_price(self):
        """Return True if purchase prices of this vendor
        must be hidden to the current user"""
        if not self:
            return False
        self.ensure_one()
        return bool(
            # sudo: field is restricted to purchase managers
            self.sudo().commercial_partner_id.hide_purchase_price
            and self.env.user.has_group("purchase_hide_price.purchase_hide_price_grp")
        )
