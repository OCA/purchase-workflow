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
from datetime import timedelta
from openerp import netsvc
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.tests.common as test_common
from .common import BaseAgreementTestMixin
from ..model.framework_agreement import AGR_PO_STATE


class TestAvailabeQty(test_common.TransactionCase, BaseAgreementTestMixin):

    """Test the function fields available_quantity"""

    def setUp(self):
        """ Create a default agreement"""
        super(TestAvailabeQty, self).setUp()
        self.commonsetUp()
        start_date = self.now + timedelta(days=10)
        start_date = start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date = self.now + timedelta(days=20)
        end_date = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        self.agreement = self.agreement_model.create(
            {'supplier_id': self.supplier_id,
             'product_id': self.product_id,
             'start_date': start_date,
             'end_date': end_date,
             'price': 77,
             'delay': 5,
             'quantity': 200}
        )
        pl = self.agreement_pl_model.create(
            {'framework_agreement_id': self.agreement.id,
             'currency_id': self.ref('base.EUR')}
        )

        self.agreement_line_model.create(
            {'framework_agreement_pricelist_id': pl.id,
             'quantity': 0,
             'price': 77.0}
        )
        self.agreement.open_agreement(strict=False)

    def test_00_noting_consumed(self):
        """Test non consumption"""
        self.assertEqual(self.agreement.available_quantity, 200)

    def test_01_150_consumed(self):
        """ test consumption of 150 units"""
        po = self.make_po_from_agreement(self.agreement, qty=150, delta_days=5)
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(
            self.env.uid,
            'purchase.order',
            po.id,
            'purchase_confirm',
            self.env.cr
        )
        po.refresh()
        self.assertIn(po.state, AGR_PO_STATE)
        self.agreement.refresh()
        self.assertEqual(self.agreement.available_quantity, 50)
