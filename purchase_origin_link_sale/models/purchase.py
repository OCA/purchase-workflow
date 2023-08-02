# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models

SO_MODEL_NAME = "sale.order"


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _selection_reference_model(self):
        res = super()._selection_reference_model() + [(SO_MODEL_NAME, "Sale Order")]
        return res

    @api.depends(lambda x: x._get_depends_compute_source_doc_ref())
    def _compute_source_doc_ref(self):
        super()._compute_source_doc_ref()
        for purchase in self:
            if not purchase.origin_reference:
                rel_sale = self.env[SO_MODEL_NAME].search(
                    [("name", "=", purchase.origin)], limit=1
                )
                if rel_sale:
                    purchase.origin_reference = "%s,%s" % (SO_MODEL_NAME, rel_sale.id)
