# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.fields import Domain


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
    _revision_unique = models.Constraint(
        "unique(unrevisioned_name, revision_number, company_id)",
        "Order Reference and revision must be unique per Company.",
    )

    def _prepare_revision_data(self, new_revision):
        vals = super()._prepare_revision_data(new_revision)
        vals.update({"state": "cancel"})
        return vals

    def action_view_revisions(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "purchase.purchase_form_action"
        )
        result["domain"] = Domain(
            [
                ("current_revision_id", "=", self.id),
                "|",
                ("active", "=", False),
                ("active", "=", True),
            ]
        )
        result["context"] = {
            "active_test": 0,
            "default_current_revision_id": self.id,
        }
        return result

    def action_back_to_current(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.current_revision_id.id,
            "view_mode": "form",
            "target": "current",
        }
