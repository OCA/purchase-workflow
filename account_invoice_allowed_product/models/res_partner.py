# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_invoice_only_allowed = fields.Boolean(
        string="Use in supplier invoices only allowed products",
        help="If checked, by default you will only be able to select products"
             " that can be supplied by this supplier when creating a supplier"
             " invoice for it. This value can be set for each invoice.")
