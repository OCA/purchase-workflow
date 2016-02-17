# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    limit_amount = fields.Integer(
        'Maximum Purchase Amount', required=True,
        help="Maximum amount after which internal validation of"
             " purchase is required.",
    )

    @api.multi
    def get_default_limit_amount(self):
        res = self.env["ir.config_parameter"].get_param(
            "purchase_internal_validation.limit_amount",
            default="5000")
        return {"limit_amount": int(res)}

    @api.multi
    def set_limit_amount(self):
        for record in self:
            self.env["ir.config_parameter"].set_param(
                "purchase_internal_validation.limit_amount",
                record.limit_amount or "5000")
