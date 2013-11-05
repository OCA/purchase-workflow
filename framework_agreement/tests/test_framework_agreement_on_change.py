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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import openerp.tests.common as test_common
from .common import BaseAgreementTestMixin
from ..model.framework_agreement import AGR_PO_STATE
from ..model.framework_agreement import FrameworkAgreementObservable


class TestAgreementOnChange(test_common.TransactionCase, BaseAgreementTestMixin):
    """Test observer on change and purchase order on chnage"""

    def setUp(self):
        """ Create a default agreement
        with 3 price line
        qty 0  price 70
        qty 200 price 60
        """
        super(TestAgreementOnChange, self).setUp()
        self.commonsetUp()
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
                                              'delay': 5,
                                              'quantity': 1500})
        self.agreement_line_model.create(cr, uid,
                                         {'framework_agreement_id': agr_id,
                                          'quantity': 0,
                                          'price': 70})
        self.agreement_line_model.create(cr, uid,
                                         {'framework_agreement_id': agr_id,
                                          'quantity': 200,
                                          'price': 60})
        self.agreement = self.agreement_model.browse(cr, uid, agr_id)
        self.po_line_model = self.registry('purchase.order.line')
        self.assertTrue(issubclass(type(self.po_line_model),
                                   FrameworkAgreementObservable))

    def test_00_observe_price_change(self):
        """Ensure that on change price observer raise correct warning

        Warning must be rose if there is a running price agreement

        """
        cr, uid = self.cr, self.uid
        res = self.po_line_model.onchange_price_obs(cr, uid, False, 20.0,
                                                    self.agreement.start_date,
                                                    self.agreement.supplier_id.id,
                                                    self.agreement.product_id.id,
                                                    qty=100)
        self.assertTrue(res.get('warning'))
        res = self.po_line_model.onchange_price_obs(cr, uid, False, 20.0,
                                                    self.now.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                    self.agreement.supplier_id.id,
                                                    self.agreement.product_id.id,
                                                    qty=100)
        self.assertFalse(res.get('warning'))

    def test_01_onchange_quantity_obs(self):
        """Ensure that on change quantity will raise warning or return price"""
        cr, uid = self.cr, self.uid
        res = self.po_line_model.onchange_quantity_obs(cr, uid, False, 200.0,
                                                       self.agreement.start_date,
                                                       self.agreement.supplier_id.id,
                                                       self.agreement.product_id.id)
        self.assertFalse(res.get('warning'))
        self.assertEqual(res.get('value', {}).get('price'), 60)
        # test there is a warning if agreement has not enought quantity
        res = self.po_line_model.onchange_quantity_obs(cr, uid, False, 20000.0,
                                                       self.agreement.start_date,
                                                       self.agreement.supplier_id.id,
                                                       self.agreement.product_id.id)
        self.assertTrue(res.get('warning'))

        res = self.po_line_model.onchange_quantity_obs(cr, uid, False, 20000.0,
                                                       self.now.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                       self.agreement.supplier_id.id,
                                                       self.agreement.product_id.id)
        self.assertFalse(res.get('warning'))

    def test_02_onchange_product_obs(self):
        """Check that change of product has correct behavior"""
        cr, uid = self.cr, self.uid
        res = self.po_line_model.onchange_product_id_obs(cr, uid, False, 200.0,
                                                         self.agreement.start_date,
                                                         self.agreement.supplier_id.id,
                                                         self.agreement.product_id.id)
        self.assertFalse(res.get('warning'))
        self.assertEqual(res.get('value', {}).get('price'), 60)

        res = self.po_line_model.onchange_product_id_obs(cr, uid, False, 20000.0,
                                                         self.agreement.start_date,
                                                         self.agreement.supplier_id.id,
                                                         self.agreement.product_id.id)
        self.assertTrue(res.get('warning'))
        self.assertEqual(res.get('value', {}).get('price'), 60)

        res = self.po_line_model.onchange_product_id_obs(cr, uid, False, 20000.0,
                                                         self.now.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                         self.agreement.supplier_id.id,
                                                         self.agreement.product_id.id)
        self.assertFalse(res.get('warning'))

        # we do the test on non agreement product

        res = self.po_line_model.onchange_product_id_obs(cr, uid, False, 20000.0,
                                                         self.agreement.start_date,
                                                         self.ref('product.product_product_33'),
                                                         self.agreement.product_id.id)
        self.assertEqual(res, {})

    def test_03_price_observer_bindings(self):
        """Check that change of price has correct behavior"""
        cr, uid = self.cr, self.uid
        res = self.po_line_model.onchange_price(cr, uid, False, 200.0,
                                                self.agreement.start_date,
                                                self.agreement.supplier_id.id,
                                                self.agreement.product_id.id,
                                                200)
        self.assertTrue(res.get('warning'))

    def test_04_product_observer_bindings(self):
        """Check that change of product has correct behavior"""
        cr, uid = self.cr, self.uid
        pl = self.agreement.supplier_id.property_product_pricelist_purchase.id,

        res = self.po_line_model.onchange_product_id(cr, uid, False,
                                                     pl,
                                                     self.agreement.product_id.id,
                                                     200,
                                                     self.agreement.product_id.uom_id.id,
                                                     self.agreement.supplier_id.id,
                                                     date_order=self.agreement.start_date[0:10])
        self.assertFalse(res.get('warning'))
