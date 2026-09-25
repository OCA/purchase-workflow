# © 2016 ForgeFlow S.L.
#   (<http://www.forgeflow.com>)
# © 2018 Hizbul Bahar <hizbul25@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _purchase_split_date_assign_domain(self, key, tz):
        domain = super()._purchase_split_date_assign_domain(key, tz)
        for key_element in key:
            if "location_dest_id" in key_element and isinstance(key_element, tuple):
                domain.append(("location_dest_id", "=", key_element[1]))
                break
        return domain
