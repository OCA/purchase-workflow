# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RequestCategory(models.Model):
    _inherit = "request.category"

    use_pr = fields.Boolean(
        string="Use PR",
        compute="_compute_use_pr",
    )

    def _compute_use_pr(self):
        for rec in self:
            rec.use_pr = rec.child_doc_option_ids.filtered_domain(
                [("model", "=", "purchase.request")]
            )

    def _has_child_doc(self):
        return super()._has_child_doc() or self.use_pr


class RequestCategoryChildDocsOption(models.Model):
    _inherit = "request.category.child.doc.option"

    model = fields.Selection(
        selection_add=[("purchase.request", "Purchase Request")],
        ondelete={"purchase.request": "cascade"},
    )
