# Copyright 2016-2019 Akretion France (https://akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    commercial_partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="partner_id.commercial_partner_id",
        store=True,
        index=True,
        string="Commercial Vendor",
    )
