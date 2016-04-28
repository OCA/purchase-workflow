#    Author: Leonardo Pistone
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

from openerp import models, fields, api


class Portfolio(models.Model):
    _name = 'framework.agreement.portfolio'
    _description = 'Agreement Portfolio'

    def _company_get(self):
        company_id = self.env['res.company']._company_default_get(self._name)
        return self.env['res.company'].browse(company_id)

    @api.returns('self')
    @api.model
    def get_from_supplier(self, supplier):
        existing_portfolios = self.search([('supplier_id', '=', supplier.id)])
        if existing_portfolios:
            return existing_portfolios[0]
        else:
            return self.create({'supplier_id': supplier.id,
                                'name': supplier.name})

    name = fields.Char('Name', required=True)
    supplier_id = fields.Many2one('res.partner', 'Supplier', required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=_company_get)
    agreement_ids = fields.One2many('framework.agreement', 'portfolio_id',
                                    'Agreements')

    _sql_constraints = [
        ('uniq_portfolio',
         'unique(supplier_id, company_id)',
         'There can be only one portfolio per supplier and company.'),
    ]
