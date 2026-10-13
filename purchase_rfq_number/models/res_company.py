# Copyright 2021 ProThai Technology Co.,Ltd. (http://prothaitechnology.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    keep_name_po = fields.Boolean(
        string="Use Same Enumeration",
        help="If this is unchecked, purchase rfq use a different sequence from "
        "Purchase orders",
        default=True,
    )
    auto_attachment_rfq = fields.Boolean(
        string="Auto Attachment RFQ",
        help="Auto attachment requests for quotation after confirm",
        default=False,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    keep_name_po = fields.Boolean(related="company_id.keep_name_po", readonly=False)
    auto_attachment_rfq = fields.Boolean(
        related="company_id.auto_attachment_rfq", readonly=False
    )
