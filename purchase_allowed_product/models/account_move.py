# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = ["account.move", "supplied.product.mixin"]
    _name = "account.move"
