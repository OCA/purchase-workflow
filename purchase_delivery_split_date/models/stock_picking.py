# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 ForgeFlow, S.L.
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import pytz

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _purchase_split_date_assign_domain(self, key, tz):
        date = key[0][1]
        wh_tz = pytz.timezone(tz) if tz else self.env.tz
        # The date is in local time
        dt_start_tz = wh_tz.localize(fields.Datetime.to_datetime(date))
        dt_start = dt_start_tz.astimezone(pytz.utc).replace(tzinfo=None)
        dt_end = fields.Datetime.add(dt_start, days=1)
        return [
            ("scheduled_date", ">=", dt_start),
            ("scheduled_date", "<", dt_end),
        ]
