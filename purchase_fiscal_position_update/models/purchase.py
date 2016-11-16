# -*- coding: utf-8 -*-
# © 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
# @author Mathieu Vatel <mathieu _at_ julius.fr>
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange('fiscal_position_id')
    def fiscal_position_change(self):
        '''Function executed by the on_change on the fiscal_position_id field
        of a purchase order ; it updates taxes on all order lines'''
        fp = self.fiscal_position_id
        for line in self.order_line:
            # product_id is a required field since v9
            taxes = line.product_id.supplier_taxes_id.filtered(
                lambda tax: tax.company_id == self.company_id)
            if fp:
                taxes = fp.map_tax(taxes)
            line.taxes_id = [(6, 0, taxes.ids)]
