# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "base.revision"]

    current_revision_id = fields.Many2one(
        comodel_name="purchase.order",
    )
    old_revision_ids = fields.One2many(
        comodel_name="purchase.order",
    )

    # Overwrite as purchase.order can be multi-company
    _sql_constraints = [
        (
            "revision_unique",
            "unique(unrevisioned_name, revision_number, company_id)",
            "Order Reference and revision must be unique per Company.",
        )
    ]

    def _prepare_revision_data(self, new_revision):
        vals = super()._prepare_revision_data(new_revision)
        vals.update({"state": "cancel"})
        return vals

    def action_view_revisions(self):
        self.ensure_one()
        action = self.env.ref("purchase.purchase_rfq")
        result = action.read()[0]
        result["domain"] = ["|", ("active", "=", False), ("active", "=", True)]
        result["context"] = {
            "active_test": 0,
            "search_default_current_revision_id": self.id,
            "default_current_revision_id": self.id,
        }
        return result
