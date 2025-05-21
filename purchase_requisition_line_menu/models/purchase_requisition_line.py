# Copyright 2025-TODAY Akretion (http://www.akretion.com/)
# @author: Renato Lima <renato.lima@akretion.com.br>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    state = fields.Selection(related="requisition_id.state", readonly=True)
