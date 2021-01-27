# -*- coding: utf-8 -*-
# © 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    check_price_on_proposal = fields.Boolean(
        help="If checked, match price on purchase proposal")
