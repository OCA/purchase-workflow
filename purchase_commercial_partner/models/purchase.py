# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    commercial_partner_id = fields.Many2one(
        'res.partner', related='partner_id.commercial_partner_id', store=True,
        index=True, string='Commercial Vendor')
