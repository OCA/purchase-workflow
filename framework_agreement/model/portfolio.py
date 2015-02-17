#    Author: Pistone
#    Copyright 2015 Camptocamp SA
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

from openerp import models, fields


class Portfolio(models.Model):
    _name = 'framework.agreement.portfolio'
    _description = 'Agreement Portfolio'

    def _company_get(self):
        return self.env['res.company']._company_default_get(self._name)

    name = fields.Char('Name', required=True)
    supplier_id = fields.Many2one('res.partner', 'Supplier', required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=_company_get)
    agreement_ids = fields.One2many('framework.agreement', 'portfolio_id',
                                    'Agreements')
