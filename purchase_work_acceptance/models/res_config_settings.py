# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_enable_wa_on_po = fields.Boolean(
        string="Enable WA on Purchase Order",
        implied_group="purchase_work_acceptance.group_enable_wa_on_po",
    )
    group_enable_wa_on_in = fields.Boolean(
        string="Enable WA on Goods Receipt",
        implied_group="purchase_work_acceptance.group_enable_wa_on_in",
    )
    group_enforce_wa_on_in = fields.Boolean(
        string="Enforce WA on Goods Receipt",
        implied_group="purchase_work_acceptance.group_enforce_wa_on_in",
    )
    group_enable_wa_on_invoice = fields.Boolean(
        string="Enable WA on Vendor Bill",
        implied_group="purchase_work_acceptance.group_enable_wa_on_invoice",
    )
    group_enforce_wa_on_invoice = fields.Boolean(
        string="Enforce WA on Vendor Bill",
        implied_group="purchase_work_acceptance.group_enforce_wa_on_invoice",
    )
