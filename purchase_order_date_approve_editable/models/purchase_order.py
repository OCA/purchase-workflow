# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    date_approve = fields.Datetime(tracking=True, readonly=False)
