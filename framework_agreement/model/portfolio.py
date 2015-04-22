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
from collections import namedtuple
from datetime import datetime

from openerp import models, fields, api, exceptions
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from openerp.tools.translate import _

AGR_PO_STATE = ('confirmed', 'approved',
                'done', 'except_picking', 'except_invoice')


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
    line_ids = fields.One2many('agreement.product.line', 'portfolio_id')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=_company_get)
    pricelist_ids = fields.One2many('product.pricelist', 'portfolio_id',
                                    'Pricelists')
    origin = fields.Char('Origin')
    start_date = fields.Date(required=True)
    end_date = fields.Date()
    draft = fields.Boolean('Is draft')
    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('future', 'Future'),
                   ('running', 'Running'),
                   ('consumed', 'Consumed'),
                   ('closed', 'Closed')],
        string='State',
        compute='_compute_state',
        search='_search_state',
        # not stored because it depends on the current date
    )
    purchase_ids = fields.One2many('purchase.order', 'portfolio_id')

    _sql_constraints = [
        ('uniq_portfolio',
         'unique(supplier_id, company_id)',
         'There can be only one portfolio per supplier and company.'),
        ('date_priority',
         'check(start_date < end_date)',
         'Start/end date inversion'),
    ]

    @api.one
    def _compute_state(self):
        """Compute the state based on dates and consumption."""
        if self.draft:
            self.state = 'draft'
        else:
            now, start, end = self._get_dates()
            if start > now:
                self.state = 'future'
            elif end and end < now:
                self.state = 'closed'
            else:  # date is good
                if all(l.available_quantity <= 0 for l in self.line_ids):
                    self.state = 'consumed'
                else:
                    self.state = 'running'

    @api.multi
    def _get_dates(self):
        """Return current time, start date and end date.

        Boiler plate as OpenERP returns string instead of date/time objects...

        :returns: namedtuple('AGDates', ['now', 'start', 'end'])
        """
        self.ensure_one()
        AGDates = namedtuple('AGDates', ['now', 'start', 'end'])
        now = fields.date.today()
        start = datetime.strptime(self.start_date, DATE_FORMAT).date()
        if self.end_date:
            end = datetime.strptime(self.end_date, DATE_FORMAT).date()
        else:
            end = None
        return AGDates(now, start, end)

    def _search_state(self, operator, value):
        """Search on the state field by evaluating on all records"""

        all_records = self.search([])

        if operator == '=':
            found_ids = [a.id for a in all_records if a.state == value]
        elif operator == 'in' and isinstance(value, list):
            found_ids = [a.id for a in all_records if a.state in value]
        elif operator in ("!=", "<>"):
            found_ids = [a.id for a in all_records if a.state != value]
        elif operator == 'not in' and isinstance(value, list):
            found_ids = [a.id for a in all_records if a.state not in value]
        else:
            raise NotImplementedError(
                'Search operator %s not implemented for value %s'
                % (operator, value)
            )
        return [('id', 'in', found_ids)]

    @api.multi
    def create_new_agreement(self):
        self.ensure_one()
        new_agreement = self.env['product.pricelist'].create({
            'name': '{}: New agreement'.format(self.name),
            'portfolio_id': self.id,
            'type': 'purchase',
            'version_id': [(0, 0, {
                'name': '{}: Main version'.format(self.name),
                'date_start': self.start_date,
                'date_end': self.end_date,
                'items_id': [(0, 0, {
                    'name': '{}: Main rule'.format(self.name),
                    'base': -2,
                    'use_agreement_prices': True,
                })],
            })],
        })

        for product_line in self.line_ids:
            self.env['product.supplierinfo'].create({
                'name': self.supplier_id.id,
                'agreement_pricelist_id': new_agreement.id,
                'product_tmpl_id': product_line.product_id.product_tmpl_id.id,
                'product_name': product_line.product_id.name,
                'product_code': product_line.product_id.code,
                'pricelist_ids': [(0, 0, {
                    'min_quantity': 1.0,
                    'price': 0.0,
                })],
            })

    @api.multi
    def get_line_for_product(self, product, quantity=0):
        self.ensure_one()
        for product_line in self.line_ids:
            if (product_line.product_id == product and
                    product_line.quantity >= quantity):
                return product_line
        return False

    @api.multi
    def is_suitable_for(self, date, product, quantity=0):
        return (self.is_valid_at_date(date) and
                self.get_line_for_product(product, quantity))

    @api.multi
    def is_valid_at_date(self, proposed_date):
        self.ensure_one()
        start = datetime.strptime(self.start_date, DATE_FORMAT)
        is_valid = start < proposed_date

        if self.end_date:
            end = datetime.strptime(self.end_date, DATE_FORMAT)
            is_valid = is_valid and proposed_date < end

        return is_valid


class AgreementProductLine(models.Model):
    _name = 'agreement.product.line'

    portfolio_id = fields.Many2one('framework.agreement.portfolio',
                                   required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    quantity = fields.Integer('Negociated quantity', required=True)
    available_quantity = fields.Integer(
        compute='_compute_available_qty',
        string='Available quantity',
        store=True,
        # this is stored because we do searches on it. However, the method
        # might be called more often than necessary (specifically, when
        # computing the state of the portfolio).
    )

    @api.depends(
        'quantity',
        'product_id',
        'portfolio_id',
        'portfolio_id.purchase_ids',
        'portfolio_id.purchase_ids.portfolio_id',
        'portfolio_id.purchase_ids.state',
        'portfolio_id.purchase_ids.order_line.product_qty'
    )
    @api.one
    def _compute_available_qty(self):
        """Compute available qty based on confirmed PO lines."""
        if isinstance(self.portfolio_id.id, models.NewId):
            return

        sql = """
            SELECT SUM(po_line.product_qty)
            FROM purchase_order_line AS po_line
            LEFT JOIN purchase_order AS po ON po_line.order_id = po.id
            WHERE po.portfolio_id = %(portfolio)s
            AND po.state IN %(states)s
            AND po.company_id = %(company)s
            AND po_line.product_id = %(product)s
        """
        self.env.cr.execute(sql, {
            'portfolio': self.portfolio_id.id,
            'states': AGR_PO_STATE,
            'company': self.portfolio_id._company_get().id,
            'product': self.product_id.id,
        })
        used_amount = self.env.cr.fetchone()[0] or 0
        self.available_quantity = self.quantity - used_amount

        if 'block_if_negative_available' in self.env.context:
            if self.available_quantity < 0:
                raise exceptions.Warning(_(
                    'Insufficient available quantity for product %s' %
                    self.product_id.name
                ))
