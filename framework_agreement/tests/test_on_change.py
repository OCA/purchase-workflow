# -*- coding: utf-8 -*-
# © 2013-2015 Camptocamp SA - Nicolas Bessi, Leonardo Pistone
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta, date
import openerp.tests.common as test_common
from openerp import exceptions, fields
from .common import BaseAgreementTestMixin


class TestAgreementOnChange(test_common.TransactionCase,
                            BaseAgreementTestMixin):
    """Test observer on change and purchase order on chnage"""

    def setUp(self):
        """ Create a default agreement
        with 3 price line
        qty 0  price 70
        qty 200 price 60
        """
        super(TestAgreementOnChange, self).setUp()
        self.commonsetUp()
        start_date = date.today() + timedelta(days=10)
        end_date = date.today() + timedelta(days=20)
        self.agreement = self.agreement_model.create({
            'portfolio_id': self.portfolio.id,
            'product_id': self.product.id,
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
            'delay': 5,
            'draft': False,
            'quantity': 1500,
        })
        self.pl = self.agreement_pl_model.create(
            {'framework_agreement_id': self.agreement.id,
             'currency_id': self.ref('base.EUR')}
        )
        self.agreement_line_model.create(
            {'framework_agreement_pricelist_id': self.pl.id,
             'quantity': 0,
             'price': 70}
        )
        self.agreement_line_model.create(

            {'framework_agreement_pricelist_id': self.pl.id,
             'quantity': 200,
             'price': 60}
        )
        self.po_line_model = self.env['purchase.order.line']

    def test_00_constraint(self):
        """Ensure that on change price observer raise correct warning

        Warning must be risen if there is a running price agreement

        """
        order = self.env['purchase.order'].create({
            'currency_id': self.ref('base.EUR'),
            'partner_id': self.supplier.id,
            'location_id': self.supplier.property_stock_customer.id,
        })
        order_line = self.po_line_model.new({
            'framework_agreement_id': self.agreement.id,
            'price_unit': 20.0,
            'product_qty': 100,
            'order_id': order.id,
        })
        exception = False
        with self.assertRaises(exceptions.UserError) as exc:
            order_line._check_line_price_unit_framework_agreement()
        if exc.exception.message:
            exception = True
        self.assertEqual(exception, True)
