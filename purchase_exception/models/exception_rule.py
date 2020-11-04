# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    purchase_ids = fields.Many2many(comodel_name="purchase.order", string="Purchases")
    model = fields.Selection(
        selection_add=[
            ("purchase.order", "Purchase order"),
            ("purchase.order.line", "Purchase order line"),
        ]
    )
