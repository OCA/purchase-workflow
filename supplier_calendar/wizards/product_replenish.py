# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import models


class ProductReplenish(models.TransientModel):
    _inherit = "product.replenish"

    def _get_date_planned(self, route_id, **kwargs):
        """Count the vendor lead time in the working days of the supplier
        calendar, like the order date."""
        if kwargs.get("supplier"):
            kwargs["supplier"] = kwargs["supplier"]._with_natural_delay(
                self.company_id or self.env.company
            )
        return super()._get_date_planned(route_id, **kwargs)
