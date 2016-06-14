# -*- coding: utf-8 -*-
# © 2013-2015 Camptocamp SA - Nicolas Bessi, Leonardo Pistone
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta, date
from openerp import fields
from openerp.tools import mute_logger
import openerp.tests.common as test_common
from .common import BaseAgreementTestMixin


class TestAgreementState(test_common.TransactionCase, BaseAgreementTestMixin):

    def setUp(self):
        super(TestAgreementState, self).setUp()
        self.commonsetUp()

    def test_00_future(self):
        """Test state of a future agreement"""
        start_date = date.today() + timedelta(days=10)
        end_date = date.today() + timedelta(days=20)

        agreement = self.agreement_model.create({
            'portfolio_id': self.portfolio.id,
            'product_id': self.product.id,
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
            'delay': 5,
            'quantity': 20,
        })

        agreement.open_agreement(strict=False)
        self.assertEqual(agreement.state, 'future')

    def test_01_past(self):
        """Test state of a past agreement"""
        start_date = date.today() - timedelta(days=20)
        end_date = date.today() - timedelta(days=10)

        agreement = self.agreement_model.create({
            'portfolio_id': self.portfolio.id,
            'product_id': self.product.id,
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
            'delay': 5,
            'quantity': 20,
        })
        agreement.open_agreement(strict=False)
        self.assertEqual(agreement.state, 'closed')

    def test_02_running(self):
        """Test state of a running agreement"""
        start_date = date.today() - timedelta(days=2)
        end_date = date.today() + timedelta(days=2)

        agreement = self.agreement_model.create({
            'portfolio_id': self.portfolio.id,
            'product_id': self.product.id,
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
            'delay': 5,
            'quantity': 20,
        })
        agreement.open_agreement(strict=False)
        self.assertEqual(agreement.state, 'running')

    def test_03_date_orderconstraint(self):
        """Test that date order is checked"""
        start_date = date.today() - timedelta(days=40)
        end_date = date.today() + timedelta(days=30)

        with mute_logger('openerp.sql_db'):
            with self.assertRaises(Exception):
                self.agreement_model.create({
                    'portfolio_id': self.portfolio.id,
                    'product_id': self.product.id,
                    'start_date': end_date,
                    'end_date': start_date,
                    'draft': False,
                    'delay': 5,
                    'quantity': 20,
                })

    def test_04_test_overlap(self):
        start_date = date.today() - timedelta(days=10)
        end_date = date.today() + timedelta(days=10)
        self.agreement_model.create({
            'portfolio_id': self.portfolio.id,
            'product_id': self.product.id,
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
            'draft': False,
            'delay': 5,
            'quantity': 20,
        })
        start_date = date.today() - timedelta(days=2)
        end_date = date.today() + timedelta(days=2)

        with mute_logger():
            with self.assertRaises(Exception):
                self.agreement_model.create({
                    'portfolio_id': self.portfolio.id,
                    'product_id': self.product.id,
                    'start_date': fields.Date.to_string(start_date),
                    'end_date': fields.Date.to_string(end_date),
                    'draft': False,
                    'delay': 5,
                    'quantity': 20,
                })

    def test_05_search_on_state(self):
        start_date = date.today() - timedelta(days=2)
        end_date = date.today() + timedelta(days=2)

        agreement = self.agreement_model.create({
            'portfolio_id': self.portfolio.id,
            'product_id': self.product.id,
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
            'delay': 5,
            'quantity': 20,
        })
        agreement.open_agreement(strict=False)
        self.assertEqual(agreement.state, 'running')
        self.assertTrue(
            self.agreement_model.search([('state', '=', 'running')]),
            msg='Search function seems broken'
        )
