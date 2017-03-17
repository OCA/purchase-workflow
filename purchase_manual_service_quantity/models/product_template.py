# -*- coding: utf-8 -*-
# Copyright 2016-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    purchase_manual_received_qty = fields.Boolean(
        string="Manually set received quantities for service product"
               " on purchase order")
