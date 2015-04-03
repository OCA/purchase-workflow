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
from openerp import fields
from openerp.tools import mute_logger
from .common import AgreementTransactionCase
from unittest2 import skip


class TestPortfolioState(AgreementTransactionCase):
    def test_future(self):
        start_date = date.today() + timedelta(days=10)
        end_date = date.today() + timedelta(days=20)

        self.portfolio.write({
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
        })
        self.assertEqual(self.portfolio.state, 'future')

    def test_past(self):
        start_date = date.today() - timedelta(days=20)
        end_date = date.today() - timedelta(days=10)

        self.portfolio.write({
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
        })
        self.assertEqual(self.portfolio.state, 'closed')

    def test_running(self):
        start_date = date.today() - timedelta(days=2)
        end_date = date.today() + timedelta(days=2)

        self.portfolio.write({
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
        })
        self.assertEqual(self.portfolio.state, 'consumed')

    def test_inverted_date_constraint(self):
        start_date = date.today() - timedelta(days=40)
        end_date = date.today() + timedelta(days=30)

        with mute_logger('openerp.sql_db'):
            with self.assertRaises(Exception):
                self.portfolio.write({
                    'start_date': end_date,
                    'end_date': start_date,
                })

    @skip('Overlap check in portfolios is unported')
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

    def test_search_on_state(self):
        start_date = date.today() - timedelta(days=2)
        end_date = date.today() + timedelta(days=2)

        self.assertEqual(
            len(self.Portfolio.search([('state', '=', 'consumed')])),
            0
        )

        self.portfolio.write({
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
        })
        self.portfolio.refresh()
        self.assertEqual(self.portfolio.state, 'consumed')
        self.assertEqual(
            len(self.Portfolio.search([('state', '=', 'consumed')])),
            1
        )
