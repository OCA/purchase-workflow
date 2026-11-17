# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    is_promotion = fields.Boolean(string="Promotion")

    @api.constrains("is_promotion", "date_start", "date_end")
    def _check_promotion_dates(self):
        for rec in self:
            if rec.is_promotion:
                if not rec.date_start or not rec.date_end:
                    raise ValidationError(
                        _("Vendor promotion requires start and end dates.")
                    )
                if rec.date_start > rec.date_end:
                    raise ValidationError(
                        _("Promotion start date must be before end date.")
                    )

    def _is_promotion_active_or_upcoming(self, date=None):
        """
        Consider Promotion is active if it's within start and end date or it's in the future
        """
        self.ensure_one()
        if not self.is_promotion:
            return False
        if not date:
            date = fields.Date.today()
        return date <= self.date_start or (self.date_start <= date <= self.date_end)
