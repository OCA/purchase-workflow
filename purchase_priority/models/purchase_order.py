# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    priority = fields.Selection(
        selection=[
            ('0', _('Low')),
            ('1', _('Medium')),
            ('2', _('High')),
            ('3', _('Very High')),
        ],
        string='Priority',
        default='1',
    )
