# -*- coding: utf-8 -*-
#    Author: Nicolas Bessi, Leonardo Pistone
#    Copyright 2013-2015 Camptocamp SA
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

from operator import attrgetter
from collections import namedtuple
from datetime import datetime
from openerp import models, fields, api, _
from openerp import exceptions
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.addons.decimal_precision as dp

AGR_PO_STATE = ('confirmed', 'approved',
                'done', 'except_picking', 'except_invoice')


class framework_agreement(models.Model):
    """Long term agreement on product price with a supplier"""

    _name = 'framework.agreement'
    _description = 'Agreement on price'

    name = fields.Char(
        'Number',
        readonly=True
    )
    supplier_id = fields.Many2one(
        'res.partner',
        'Supplier',
        related='portfolio_id.supplier_id',
        readonly=True,
    )
    portfolio_id = fields.Many2one(
        'framework.agreement.portfolio',
        'Portfolio',
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        required=True
    )
    origin = fields.Char('Origin')
    start_date = fields.Date('Begin of Agreement')
    end_date = fields.Date('End of Agreement')
    delay = fields.Integer('Lead time in days')
    quantity = fields.Integer(
        'Negociated quantity',
        required=True
    )
    framework_agreement_pricelist_ids = fields.One2many(
        'framework.agreement.pricelist',
        'framework_agreement_id',
        'Price lists'
    )
    available_quantity = fields.Integer(
        compute='_get_available_qty',
        string='Available quantity',
        readonly=True,
        store=True,
        default=0,
    )

    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('future', 'Future'),
                   ('running', 'Running'),
                   ('consumed', 'Consumed'),
                   ('closed', 'Closed')],
        string='State',
        compute='_get_state',
        search='_search_state',
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        related='portfolio_id.company_id',
        readonly=True,
    )
    draft = fields.Boolean('Is draft')

    purchase_line_ids = fields.One2many(
        comodel_name='purchase.order.line',
        inverse_name='framework_agreement_id'
    )

    payment_term_id = fields.Many2one('account.payment.term', 'Payment Term')

    incoterm_id = fields.Many2one(
        'stock.incoterms',
        'Incoterm',
        help="International Commercial Terms are a series of predefined "
        "commercial terms used in international transactions.")

    incoterm_address = fields.Char('Incoterm Address')

    delivery_remark = fields.Text('Delivery Remarks')

    clauses = fields.Html('Clauses')

    shipment_origin_id = fields.Many2one('res.partner', 'Shipment Origin')

    @api.model
    def get_agreement_domain(self, product_id, qty, portfolio_id=None,
                             date_planned=None, incoterm_id=None,
                             incoterm_address=None):
        ag_domain = [
            ('draft', '=', False),
            ('product_id', '=', product_id),
            ('available_quantity', '>=', qty or 0.0),
        ]
        if portfolio_id:
            ag_domain += [('portfolio_id', '=', portfolio_id)]
        if date_planned:
            ag_domain += [
                ('start_date', '<=', date_planned),
                ('end_date', '>=', date_planned),
            ]
        if incoterm_id:
            ag_domain += [('incoterm_id', '=', incoterm_id)]
        if incoterm_address:
            ag_domain += [('incoterm_address', '=', incoterm_address)]

        return ag_domain

    @api.model
    def _check_running_date(self, agreement):
        """ Returns agreement state based on date.

        Available qty is ignored in this method

        :param agreement: an agreement record

        :return: - "running" if now is between,
                  - "future" if agreement is in future,
                  - "closed" if agreement is outdated
        :rtype: str
        """
        now, start, end = self._get_dates(agreement)
        if start > now:
            return 'future'
        elif end < now:
            return 'closed'
        elif start <= now <= end:
            return 'running'
        else:
            raise ValueError('Agreement start/end dates are incorrect')

    @api.model
    def _get_dates(self, agreement):
        """Return current time, start date and end date of agreement

        Boiler plate as OpenERP returns string instead of date/time objects...

        :param agreement: agreement record

        :returns: namedtuple('AGDates', ['now', 'start', 'end'])
        :rtype: namedtuple('AGDates', ['now', 'start', 'end'])
        """
        AGDates = namedtuple('AGDates', ['now', 'start', 'end'])
        now = fields.date.today()
        start = datetime.strptime(agreement.start_date,
                                  DEFAULT_SERVER_DATE_FORMAT)
        end = datetime.strptime(agreement.end_date,
                                DEFAULT_SERVER_DATE_FORMAT)
        return AGDates(now, start.date(), end.date())

    def _search_state(self, operator, value):
        """Search on the state field by evaluating on all records"""

        agreements = self.search([])

        if operator == '=':
            found_ids = [a.id for a in agreements if a.state == value]
        elif operator == 'in' and isinstance(value, list):
            found_ids = [a.id for a in agreements if a.state in value]
        elif operator in ("!=", "<>"):
            found_ids = [a.id for a in agreements if a.state != value]
        elif operator == 'not in' and isinstance(value, list):
            found_ids = [a.id for a in agreements if a.state not in value]
        else:
            raise NotImplementedError(
                'Search operator %s not implemented for value %s'
                % (operator, value)
            )
        return [('id', 'in', found_ids)]

    @api.multi
    def _compute_available_qty(self):
        """Compute available qty of current agreements.

        Consumption is based on confirmed po lines.
        Please refer to function field documentation for more details.

        """
        for agreement in self:
            company = agreement.portfolio_id._company_get()
            if isinstance(agreement.id, models.NewId):
                agreement.available_quantity = 0
                continue
            variant_ids = tuple(x.id for x
                                in agreement.product_id.product_variant_ids)
            sql = """SELECT SUM(po_line.product_qty)
               FROM purchase_order_line AS po_line
            LEFT JOIN purchase_order AS po ON po_line.order_id = po.id
            WHERE po_line.framework_agreement_id = %s
            AND po_line.product_id in %s
            AND po.partner_id = %s
            AND po.state IN %s
            AND po.company_id = %s"""
            self.env.cr.execute(sql, (agreement.id,
                                      variant_ids,
                                      agreement.portfolio_id.supplier_id.id,
                                      AGR_PO_STATE,
                                      company.id))
            amount = self.env.cr.fetchone()[0]
            if amount is None:
                amount = 0
            agreement.available_quantity = agreement.quantity - amount

    @api.depends('quantity',
                 'purchase_line_ids.framework_agreement_id',
                 'purchase_line_ids.order_id.state',
                 'purchase_line_ids',
                 'purchase_line_ids.product_qty')
    @api.multi
    def _get_available_qty(self):
        """Compute available qty of current agreements.

        Consumption is based on confirmed po lines.
        Please refer to function field documentation for more details.

        """
        self._compute_available_qty()

    @api.multi
    def _compute_state(self):
        """ Compute current state of agreement based on date and consumption

        Please refer to function field documentation for more details.

        """
        for agreement in self:
            if isinstance(agreement.id, models.NewId):
                agreement.state = 'draft'
                continue
            if (agreement.draft or not agreement.start_date or
                    not agreement.end_date):
                agreement.state = 'draft'
                continue
            dates_state = self._check_running_date(agreement)
            if dates_state == 'running':
                if agreement.available_quantity <= 0:
                    agreement.state = 'consumed'
                else:
                    agreement.state = 'running'
            else:
                agreement.state = dates_state

    @api.multi
    @api.depends('quantity',
                 'purchase_line_ids.framework_agreement_id',
                 'purchase_line_ids.order_id.state',
                 'purchase_line_ids',
                 'purchase_line_ids.product_qty')
    # same dependencies as available_quantity
    def _get_state(self):
        """ Compute current state of agreement based on date and consumption

        Please refer to function field documentation for more details.

        """
        self._compute_state()

    @api.multi
    def open_agreement(self, strict=True):
        """Open agreement

        Agreement goes from state draft to X
        """

        for agr in self:
            mandatory = [agr.start_date,
                         agr.end_date,
                         agr.framework_agreement_pricelist_ids]
            if not all(mandatory) and strict:
                raise exceptions.Warning(_(
                    'Data are missing. Please enter dates and prices'
                ))
        self.write({'draft': False})

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """We want to have increment sequence only at creation

        When set by a default in a o2m form default consume sequence.
        But we do not want to use no_gap sequence

        """
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'framework.agreement'
        )
        return super(framework_agreement, self).create(vals)

    @api.one
    @api.constrains('supplier_id', 'product_id', 'start_date', 'end_date',
                    'company_id', 'incoterm_id', 'incoterm_address')
    def check_overlap(self):
        """Check that there are no similar agreements at the same time.

        Depending on the one_agreement_per_product flag on the company,
        agreements from different companies are tolerated or not.

        """
        date_domain = [
            ('start_date', '<=', self.end_date),
            ('end_date', '>=', self.start_date),
        ]

        overlap = self.search(
            date_domain +
            [
                ('draft', '=', False),
                ('product_id', '=', self.product_id.id),
                ('incoterm_id', '=', self.incoterm_id.id),
                ('incoterm_address', '=', self.incoterm_address),
                ('id', '!=', self.id),
            ]
        )

        if self.company_id.one_agreement_per_product:
            # in strict mode, any overlap is bad
            if overlap:
                raise exceptions.ValidationError(
                    _('There is already is a running agreement for '
                      'product %s')) % self.product_id.name
        else:
            # in non-strict mode, same-supplier overlap is bad
            if any(o.supplier_id == self.supplier_id for o in overlap):
                raise exceptions.ValidationError(
                    _('There can only be one agreement for a given '
                      'supplier, incoterm, incoterm address and product'))

    _sql_constraints = [('date_priority',
                         'check(start_date < end_date)',
                         'Start/end date inversion')]

    @api.model
    def get_all_product_agreements(self, product_id, lookup_dt, qty=None):
        """Get the all the active agreement of a given product at a given date

        :param product_id: product id of the product
        :param lookup_dt: date string of the lookup date
        :param qty: quantity that should be available if parameter is
                    passed and qty is insuffisant no agreement
                    would be returned

        :returns: a list of corresponding agreements or None

        """
        search_args = [('product_id', '=', product_id),
                       ('start_date', '<=', lookup_dt),
                       ('end_date', '>=', lookup_dt),
                       ('draft', '=', False)]
        if qty:
            search_args.append(('available_quantity', '>=', qty))
        return self.search(search_args)

    @api.model
    def get_cheapest_agreement_for_qty(self, product_id, date, qty,
                                       currency=None):
        """Return the cheapest agreement that has enough available qty.

        If not enough quantity fallback on the cheapest agreement available
        for quantity.

        :param product_id: id of the product
        :param date: lookup date
        :param qty: lookup qty
        :param currency: currency record to make price convertion

        :return: cheapest agreement and qty state
        :rtype: namedtuple('Cheapest', ['cheapest_agreement', 'enough'])

        """
        Cheapest = namedtuple('Cheapest', ['cheapest_agreement', 'enough'])
        agreements = self.get_all_product_agreements(product_id,
                                                     date,
                                                     qty)
        if not agreements:
            return Cheapest(None, None)
        agreements = sorted(agreements,
                            key=lambda x: x.get_price(qty, currency=currency))
        enough = True
        cheapest_agreement = None
        for agr in agreements:
            if agr.available_quantity >= qty:
                cheapest_agreement = agr
                break
        if not cheapest_agreement:
            cheapest_agreement = agreements[0]
            enough = False
        return Cheapest(cheapest_agreement, enough)

    @api.model
    def get_product_agreement(self, product_id, supplier_id,
                              lookup_dt, qty=None):
        """Get the matching agreement for a given product/supplier at date
        :param product_id: id of the product
        :param supplier_id: supplier to look for agreement
        :param lookup_dt: date string of the lookup date
        :param qty: quantity that should be available if parameter is
        passed and qty is insuffisant no aggrement would be returned

        :returns: a corresponding agreement or None

        """
        search_args = [('product_id', '=', product_id),
                       ('supplier_id', '=', supplier_id),
                       ('start_date', '<=', lookup_dt),
                       ('end_date', '>=', lookup_dt),
                       ('draft', '=', False)]
        if qty:
            search_args.append(('available_quantity', '>=', qty))
        agreement_ids = self.search(search_args)
        if len(agreement_ids) > 1:
            raise exceptions.Warning(
                _('Many agreements found for the product with id %s'
                  ' at date %s') % (product_id, lookup_dt))
        if agreement_ids:
            return agreement_ids[0]
        return None

    @api.multi
    def has_currency(self, currency):
        """Predicate that check that agreement has a given currency pricelist

        :returns: boolean (True if a price list in given currency is present)

        """
        plists = self.framework_agreement_pricelist_ids
        return any(x for x in plists if x.currency_id == currency)

    @api.model
    def _get_pricelist_lines(self, agreement, currency):
        plists = agreement.framework_agreement_pricelist_ids
        # we do not use has_agreement for performance reason
        # Python cookbook idiom
        plist = next((x for x in plists if x.currency_id == currency), None)
        if not plist:
            raise exceptions.Warning(
                _('Missing Agreement price list '
                  'Please set a price list in currency %s for agreement %s') %
                (currency.name, agreement.name)
            )
        return plist.framework_agreement_line_ids

    @api.multi
    def get_price(self, qty=0, currency=None):
        """Return price negociated for quantity

        :param currency: currency record
        :param qty: qty to lookup


        :returns: price float

        """
        self.ensure_one()
        if not currency:
            currency = self.company_id.currency_id
        lines = self._get_pricelist_lines(self, currency)
        lines = [x for x in lines]
        lines.sort(key=attrgetter('quantity'), reverse=True)
        for line in lines:
            if qty >= line.quantity:
                return line.price
        return lines[-1].price

    @api.model
    def _get_currency(self, supplier_id, pricelist_id):
        """Helper to retrieve correct currency.

        It will look for currency on supplied pricelist if available
        else it will look for partner pricelist currency

        :param supplier_id: supplier of agreement
        :param pricelist_id: primary price list

        :returns: currency browse record

        """

        plist_obj = self.env['product.pricelist']
        partner_obj = self.env['res.partner']
        if pricelist_id:
            plist = plist_obj.browse(pricelist_id)
            return plist.currency_id
        partner = partner_obj.browse(supplier_id)
        if not partner.property_product_pricelist_purchase:
            raise exceptions.Warning(
                _('No pricelist found'
                  'Please set a pricelist on PO or supplier %s') %
                partner.name
            )
        return partner.property_product_pricelist_purchase.currency_id


class framework_agreement_pricelist(models.Model):
    """Price list container"""

    _name = "framework.agreement.pricelist"
    _rec_name = 'currency_id'
    framework_agreement_id = fields.Many2one(
        'framework.agreement',
        'Agreement',
        required=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        required=True
    )
    framework_agreement_line_ids = fields.One2many(
        'framework.agreement.line',
        'framework_agreement_pricelist_id',
        'Price lines',
        required=True
    )


class framework_agreement_line(models.Model):
    """Price list line of framework agreement
    that contains price and qty"""

    _name = 'framework.agreement.line'
    _description = 'Framework agreement line'
    _rec_name = "quantity"
    _order = "quantity"

    framework_agreement_pricelist_id = fields.Many2one(
        'framework.agreement.pricelist',
        'Price list',
        required=True
    )
    quantity = fields.Integer(
        'Quantity',
        required=True
    )

    price = fields.Float(
        string='Negociated price',
        required=True,
        digits=dp.get_precision('Product Price'),
    )
