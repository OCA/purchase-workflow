from odoo import api, models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    @api.model
    def _get_under_validation_exceptions(self):
        """Extend for more field exceptions."""
        res = super()._get_under_validation_exceptions()
        res.append("purchase_group_id")
        return res
