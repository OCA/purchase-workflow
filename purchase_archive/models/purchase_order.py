# Copyright 2018 brain-tec AG - Raúl Martín
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    active = fields.Boolean(default=True)
