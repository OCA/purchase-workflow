# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>

from odoo import fields, models, SUPERUSER_ID


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def dt2date(self, datetime):
        """Convert a datetime to date respecting tz"""
        # TODO: extract the tz field on the warehouse from the module
        # sale_cutoff_time_delivery in OCA/sale-workflow to make a generic module
        # on which this module can depend on. At the moment, we take the tz of the
        # SUPERUSER if defined. This is safer than the tz of the user
        # (purchaser) that can be freely modified by the user.
        tz = self.env["res.users"].sudo().browse(SUPERUSER_ID).tz
        tz = tz or self.env.context.get("tz") or self.env.user.tz
        self = self.with_context(tz=tz)
        return fields.Date.context_today(self, datetime)
