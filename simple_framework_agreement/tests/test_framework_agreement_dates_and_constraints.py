# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2013 Camptocamp SA
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
from datetime import datetime, timedelta
import openerp.tests.common as test_common
from openerp.osv import fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class BaseAgreementTest(test_common.TransactionCase):

    def setUp(self):
        super(BaseAgreementTest, self).setUp()
        cr, uid = self.cr, self.uid
        self.agreement_model = self.registry('framework.agreement')
        self.now = datetime.strptime(fields.datetime.now(),
                                     DEFAULT_SERVER_DATETIME_FORMAT)
        self.product_id = self.registry('product.product').create(cr, uid,
                                                                  {'name': 'test_1',
                                                                   'list_price': 10.00})
        self.supplier_id = self.registry('res.partner').create(cr, uid, {'name': 'toto',
                                                                         'supplier': 'True'})

    def tearDown(self):
        super(BaseAgreementTest, self).tearDown()


class TestAgreementState(BaseAgreementTest):

    def test_00_future(self):
        """Test state of a future agreement"""
        cr, uid = self.cr, self.uid
        start_date = self.now + timedelta(days=10)
        start_date = start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = self.now + timedelta(days=20)
        end_date = end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        agr_id = self.agreement_model.create(cr, uid,
                                             {'supplier_id': self.supplier_id,
                                              'product_id': self.product_id,
                                              'start_date': start_date,
                                              'end_date': end_date,
                                              'price': 77,
                                              'delay': 5,
                                              'quantity': 20})
        agreement = self.agreement_model.browse(cr, uid, agr_id)
        self.assertEqual(agreement.state, 'future')

    def test_01_past(self):
        """Test state of a past agreement"""
        cr, uid = self.cr, self.uid
        start_date = self.now - timedelta(days=20)
        start_date = start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = self.now - timedelta(days=10)
        end_date = end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        agr_id = self.agreement_model.create(cr, uid,
                                             {'supplier_id': self.supplier_id,
                                              'product_id': self.product_id,
                                              'start_date': start_date,
                                              'end_date': end_date,
                                              'price': 77,
                                              'delay': 5,
                                              'available_quantity': 20,
                                              'quantity': 20})
        agreement = self.agreement_model.browse(cr, uid, agr_id)
        self.assertEqual(agreement.state, 'closed')

    def test_02_running(self):
        """Test state of a running agreement"""
        cr, uid = self.cr, self.uid
        start_date = self.now - timedelta(days=2)
        start_date = start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = self.now + timedelta(days=2)
        end_date = end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        agr_id = self.agreement_model.create(cr, uid,
                                             {'supplier_id': self.supplier_id,
                                              'product_id': self.product_id,
                                              'start_date': start_date,
                                              'end_date': end_date,
                                              'price': 77,
                                              'delay': 5,
                                              'available_quantity': 20,
                                              'quantity': 20})
        agreement = self.agreement_model.browse(cr, uid, agr_id)
        self.assertEqual(agreement.state, 'running')

    def test_03_date_orderconstraint(self):
        """Test that date order is checked"""
        cr, uid = self.cr, self.uid
        start_date = self.now - timedelta(days=40)
        start_date = start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = self.now + timedelta(days=30)
        end_date = end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        with self.assertRaises(Exception) as constraint:
            self.agreement_model.create(cr, uid,
                                        {'supplier_id': self.supplier_id,
                                         'product_id': self.product_id,
                                         'start_date': end_date,
                                         'end_date': start_date,
                                         'price': 77,
                                         'delay': 5,
                                         'available_quantity': 20,
                                         'quantity': 20})

    def test_04_test_overlapp(self):
        """Test overlapping agreement for same supplier constraint"""
        cr, uid = self.cr, self.uid
        start_date = self.now - timedelta(days=10)
        start_date = start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = self.now + timedelta(days=10)
        end_date = end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.agreement_model.create(cr, uid,
                                    {'supplier_id': self.supplier_id,
                                     'product_id': self.product_id,
                                     'start_date': start_date,
                                     'end_date': end_date,
                                     'price': 77,
                                     'delay': 5,
                                     'available_quantity': 20,
                                     'quantity': 20})
        start_date = self.now - timedelta(days=2)
        start_date = start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = self.now + timedelta(days=2)
        end_date = end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        with self.assertRaises(Exception) as constraint:
            self.agreement_model.create(cr, uid,
                                        {'supplier_id': self.supplier_id,
                                         'product_id': self.product_id,
                                         'start_date': start_date,
                                         'end_date': end_date,
                                         'price': 77,
                                         'delay': 5,
                                         'available_quantity': 20,
                                         'quantity': 20})
