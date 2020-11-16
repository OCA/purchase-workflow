# © 2017 Today Mourad EL HADJ MIMOUNE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SuppliedProductMixin(models.AbstractModel):
    _name = "supplied.product.mixin"
    _description = "Mixin for documents that want to restrict products"

    use_only_supplied_product = fields.Boolean(
        string="Use only allowed products",
        help="If checked, only the products provided by this supplier "
        "will be shown.",
    )

    @api.onchange("partner_id")
    def _onchange_partner_id_supplied_product(self):
        self.use_only_supplied_product = (
            self.partner_id.use_only_supplied_product
            or self.partner_id.commercial_partner_id.use_only_supplied_product
        )
