# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    free_shipping_amount = fields.Float(
        string='Free Shipping Minimum Amount',
        related_sudo=False,
        related='partner_id.free_shipping_amount',
        store=True)
