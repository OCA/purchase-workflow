##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

from odoo import models, api, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Private section
    @api.model
    # Later, we may want to implement other valid_psi options
    def _valid_psi(self, method):
        self.ensure_one()
        if method == 'first':
            return self._first_valid_psi()
        elif method == 'all':
            return self._all_valid_psi()
        else:
            return False

    @api.model
    def _all_valid_psi(self):
        self.ensure_one()
        today = fields.Date.today()
        if not self.product_tmpl_id.seller_ids:
            return False
        valid_si = self.product_tmpl_id.seller_ids.filtered(
            lambda si, t=today: ((not si.date_start or si.date_start <= t) and
                                 (not si.date_end or si.date_end >= t)))
        return valid_si

    @api.model
    def _first_valid_psi(self):
        self.ensure_one()
        if not self.product_tmpl_id.seller_ids:
            return False
        valid_si = self._all_valid_psi()[0]
        seq = min([si.sequence for si in valid_si])
        return valid_si.filtered(lambda si, seq=seq: si.sequence == seq)
