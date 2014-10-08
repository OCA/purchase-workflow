# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2013-2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import api, models, fields


class PurchaseCancelReason(models.Model):
    _name = "purchase.cancel_reason"

    name = fields.Char('Reason', size=64, required=True, translate=True)
    type = fields.Selection(
        [('rfq', 'RFQ/Bid'),
         ('purchase', 'Purchase Order')],
        'Type', required=True)
    nounlink = fields.Boolean('No unlink')

    @api.one
    def unlink(self):
        """ Prevent to unlink records that are used in the code
        """
        if self.nounlink:
            return True
        else:
            return super(PurchaseCancelReason, self).unlink()
