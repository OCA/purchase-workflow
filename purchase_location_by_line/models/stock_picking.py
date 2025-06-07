# © 2016 ForgeFlow S.L.
#   (<http://www.forgeflow.com>)
# © 2018 Hizbul Bahar <hizbul25@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.osv import expression


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _purchase_split_date_assign_domain(self, key, tz):
        domain = super()._purchase_split_date_assign_domain(key, tz)
        for key_element in key:
            if (
                "location_dest_id" in key_element.keys()
                and key_element["location_dest_id"]
            ):
                domain = expression.AND(
                    [
                        domain,
                        [("location_dest_id", "=", key_element["location_dest_id"])],
                    ]
                )
                break
        return domain
