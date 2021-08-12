# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    partner_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Address",
        readonly=True,
        help="This address version is fixed when this order is confirmed.",
    )

    def button_confirm(self):
        for order in self:
            address = order.partner_id._version_create()
            address._write(
                {
                    "name": address.name.replace("copy", order.name),
                    "display_name": address.display_name.replace("copy", order.name),
                }
            )
            order.partner_address_id = address
        return super().button_confirm()
