# -*- coding: utf-8 -*-
# Copyright 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2014 Akretion (http://www.akretion.com)
# Copyright 2016 - Tecnativa - Angel Moya <odoo@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _


class purchase_order(models.Model):
    _inherit = "purchase.order"

    @api.onchange('fiscal_position_id')
    def onchange_fiscal_position_id(self):
        for line in self.order_line:
            line.onchange_product_id()
