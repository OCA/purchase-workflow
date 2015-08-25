# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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

from osv import orm, fields


class purchase_internal_validation_settings(orm.TransientModel):
    _inherit = 'purchase.config.settings'
    _columns = {
        'limit_amount': fields.integer(
            'Maximum Purchase Amount', required=True,
            help="Maximum amount after which internal validation of"
                 " purchase is required.",
        ),
    }

    def get_default_limit_amount(self, cr, uid, ids, context=None):
        res = self.pool["ir.config_parameter"].get_param(
            cr, uid, "purchase_internal_validation.limit_amount",
            default="5000", context=context)
        return {"limit_amount": int(res)}

    def set_limit_amount(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            self.pool["ir.config_parameter"].set_param(
                cr, uid, "purchase_internal_validation.limit_amount",
                record.limit_amount or "5000")
