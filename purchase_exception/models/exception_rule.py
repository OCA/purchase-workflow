# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('purchase', 'Purchase')],
    )
    model = fields.Selection(
        selection_add=[
            ('purchase.order', 'Purchase order'),
            ('purchase.order.line', 'Purchase order line'),
        ])
