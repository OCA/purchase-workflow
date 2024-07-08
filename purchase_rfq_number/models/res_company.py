# Copyright 2021 ProThai Technology Co.,Ltd. (http://prothaitechnology.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    keep_name_po = fields.Boolean(
        string="Use Same Enumeration",
        help="If this is unchecked, purchase RFQs use a different sequence from "
        "confirmed orders",
        default=True,
    )
    auto_attachment_rfq = fields.Boolean(
        string="Auto Attachment RFQ",
        help="Store the purchase RFQ PDF right before confirmation of the PO",
        default=False,
    )
