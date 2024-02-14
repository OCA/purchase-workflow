# © 2017 Today Mourad EL HADJ MIMOUNE @ Akretion
# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SuppliedProductMixin(models.AbstractModel):
    _name = "supplied.product.mixin"
    _description = "Mixin for documents that want to restrict products"

    use_only_supplied_product = fields.Boolean(
        string="Use only allowed products",
        compute="_compute_partner_id_supplied_product",
        store=True,
        readonly=False,
        help="If checked, only the products provided by this supplier "
        "will be shown.",
    )

    @api.depends("partner_id")
    def _compute_partner_id_supplied_product(self):
        for record in self:
            record.use_only_supplied_product = (
                record.partner_id.use_only_supplied_product
                or record.partner_id.commercial_partner_id.use_only_supplied_product
            )
