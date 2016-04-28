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

from datetime import timedelta, date
from openerp import exceptions, fields
import openerp.tests.common as test_common
from .common import BaseAgreementTestMixin


class TestAgreementPriceList(test_common.TransactionCase,
                             BaseAgreementTestMixin):
    """Test observer on_change and purchase order on_change"""

    def setUp(self):
        """ Create a default agreement
        with 3 price line
        qty 0  price 70
        qty 200 price 60
        qty 500 price 50
        qty 1000 price 45
        """
        super(TestAgreementPriceList, self).setUp()
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

        pl = self.agreement_pl_model.create(
            {'framework_agreement_id': self.agreement.id,
             'currency_id': self.ref('base.EUR')}
        )

        self.agreement_line_model.create(
            {'framework_agreement_pricelist_id': pl.id,
             'quantity': 0,
             'price': 70.0}
        )
        self.agreement_line_model.create(
            {'framework_agreement_pricelist_id': pl.id,
             'quantity': 200,
             'price': 60.0}
        )
        self.agreement_line_model.create(
            {'framework_agreement_pricelist_id': pl.id,
             'quantity': 500,
             'price': 50.0}
        )
        self.agreement_line_model.create(
            {'framework_agreement_pricelist_id': pl.id,
             'quantity': 1000,
             'price': 45.0}
        )
        self.agreement.refresh()

    def test_00_test_qty(self):
        """Test if barem retrieval is correct"""
        self.assertEqual(
            self.agreement.get_price(0, currency=self.browse_ref('base.EUR')),
            70.0
        )
        self.assertEqual(
            self.agreement.get_price(
                100,
                currency=self.browse_ref('base.EUR')
            ),
            70.0
        )
        self.assertEqual(
            self.agreement.get_price(
                200,
                currency=self.browse_ref('base.EUR')
            ),
            60.0
        )
        self.assertEqual(
            self.agreement.get_price(
                210,
                currency=self.browse_ref('base.EUR')
            ),
            60.0
        )
        self.assertEqual(
            self.agreement.get_price(
                500,
                currency=self.browse_ref('base.EUR')),
            50.0
        )
        self.assertEqual(
            self.agreement.get_price(
                800,
                currency=self.browse_ref('base.EUR')
            ),
            50.0
        )
        self.assertEqual(
            self.agreement.get_price(
                999,
                currency=self.browse_ref('base.EUR')
            ),
            50.0
        )
        self.assertEqual(
            self.agreement.get_price(
                1000,
                currency=self.browse_ref('base.EUR')
            ),
            45.0
        )
        self.assertEqual(
            self.agreement.get_price(
                10000,
                currency=self.browse_ref('base.EUR')
            ),
            45.0
        )
        self.assertEqual(
            self.agreement.get_price(
                -10,
                currency=self.browse_ref('base.EUR')
            ),
            70.0
        )

    def test_01_failed_wrong_currency(self):
        """Tests that wrong currency raise an exception"""
        with self.assertRaises(exceptions.Warning):
            self.agreement.get_price(0, currency=self.browse_ref('base.USD'))
