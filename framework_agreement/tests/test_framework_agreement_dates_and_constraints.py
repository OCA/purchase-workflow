# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2013, 2014 Camptocamp SA
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
from datetime import timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import mute_logger
import openerp.tests.common as test_common
from .common import BaseAgreementTestMixin


class TestAgreementState(test_common.TransactionCase, BaseAgreementTestMixin):

    def setUp(self):
        super(TestAgreementState, self).setUp()
        self.commonsetUp()

    def test_00_future(self):
        """Test state of a future agreement"""
        start_date = self.now + timedelta(days=10)
        start_date = start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date = self.now + timedelta(days=20)
        end_date = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        agreement = self.agreement_model.create(
            {'supplier_id': self.supplier_id,
             'product_id': self.product_id,
             'start_date': start_date,
             'end_date': end_date,
             'delay': 5,
             'quantity': 20}
        )

        agreement.open_agreement(strict=False)
        self.assertEqual(agreement.state, 'future')

    def test_01_past(self):
        """Test state of a past agreement"""
        start_date = self.now - timedelta(days=20)
        start_date = start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date = self.now - timedelta(days=10)
        end_date = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        agreement = self.agreement_model.create(
            {'supplier_id': self.supplier_id,
             'product_id': self.product_id,
             'start_date': start_date,
             'end_date': end_date,
             'delay': 5,
             'quantity': 20}
        )
        agreement.open_agreement(strict=False)
        self.assertEqual(agreement.state, 'closed')

    def test_02_running(self):
        """Test state of a running agreement"""
        start_date = self.now - timedelta(days=2)
        start_date = start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date = self.now + timedelta(days=2)
        end_date = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        agreement = self.agreement_model.create(
            {'supplier_id': self.supplier_id,
             'product_id': self.product_id,
             'start_date': start_date,
             'end_date': end_date,
             'delay': 5,
             'quantity': 20}
        )
        agreement.open_agreement(strict=False)
        self.assertEqual(agreement.state, 'running')

    def test_03_date_orderconstraint(self):
        """Test that date order is checked"""
        start_date = self.now - timedelta(days=40)
        start_date = start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date = self.now + timedelta(days=30)
        end_date = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        # XXX for some reason this is assertRaises is not affected by
        # odoo/odoo#3056. The next one in this file is.
        with mute_logger('openerp.sql_db'):
            with self.assertRaises(Exception):
                self.agreement_model.create(
                    {'supplier_id': self.supplier_id,
                     'product_id': self.product_id,
                     'start_date': end_date,
                     'end_date': start_date,
                     'draft': False,
                     'delay': 5,
                     'quantity': 20}
                )

    def test_04_test_overlapp(self):
        """Test overlapping agreement for same supplier constraint"""
        start_date = self.now - timedelta(days=10)
        start_date = start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date = self.now + timedelta(days=10)
        end_date = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        self.agreement_model.create(
            {'supplier_id': self.supplier_id,
             'product_id': self.product_id,
             'start_date': start_date,
             'end_date': end_date,
             'draft': False,
             'delay': 5,
             'quantity': 20}
        )
        start_date = self.now - timedelta(days=2)
        start_date = start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date = self.now + timedelta(days=2)
        end_date = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        # XXX disable this test to work around odoo/odoo#3056
        if False:
            with mute_logger():
                with self.assertRaises(Exception):
                    self.agreement_model.create(
                        {'supplier_id': self.supplier_id,
                         'product_id': self.product_id,
                         'start_date': start_date,
                         'end_date': end_date,
                         'draft': False,
                         'delay': 5,
                         'quantity': 20}
                    )

    def test_05_search_on_state(self):
        start_date = self.now - timedelta(days=2)
        start_date = start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date = self.now + timedelta(days=2)
        end_date = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        agreement = self.agreement_model.create(
            {'supplier_id': self.supplier_id,
             'product_id': self.product_id,
             'start_date': start_date,
             'end_date': end_date,
             'delay': 5,
             'quantity': 20}
        )
        agreement.open_agreement(strict=False)
        self.assertEqual(agreement.state, 'running')
        self.assertTrue(
            self.agreement_model.search([('state', '=', 'running')]),
            msg='Search function seems broken'
        )
