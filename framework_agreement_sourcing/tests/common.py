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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.tests.common as test_common
from openerp.addons.logistic_requisition.tests import logistic_requisition
from openerp.addons.framework_agreement.tests.common import BaseAgreementTestMixin


class CommonSourcingSetUp(test_common.TransactionCase, BaseAgreementTestMixin):

    def setUp(self):
        """
        Setup a standard configuration for test
        """
        super(CommonSourcingSetUp, self).setUp()
        self.commonsetUp()
        self.requisition_model = self.registry('logistic.requisition')
        self.requisition_line_model = self.registry('logistic.requisition.line')
        self.source_line_model = self.registry('logistic.requisition.source')
        self.make_common_agreements()
        self.make_common_requisition()

    def make_common_requisition(self):
        """Create a standard logistic requisition"""
        start_date = self.now + timedelta(days=12)
        start_date = start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        req = {
            'partner_id': self.ref('base.res_partner_1'),
            'consignee_id': self.ref('base.res_partner_3'),
            'date_delivery': start_date,
            'date': start_date,
            'user_id': self.uid,
            'budget_holder_id': self.uid,
            'finance_officer_id': self.uid,
        }
        agr_line = {
            'product_id': self.product_id,
            'requested_qty': 100,
            'requested_uom_id': self.ref('product.product_uom_unit'),
            'date_delivery': self.now.strftime(DEFAULT_SERVER_DATE_FORMAT),
            'budget_tot_price': 100000000,
        }
        other_line = {
            'product_id': self.ref('product.product_product_7'),
            'requested_qty': 10,
            'requested_uom_id': self.ref('product.product_uom_unit'),
            'date_delivery': self.now.strftime(DEFAULT_SERVER_DATE_FORMAT),
            'budget_tot_price': 100000000,
        }

        requisition_id = logistic_requisition.create(self, req)
        logistic_requisition.add_line(self, requisition_id,
                                      agr_line)
        logistic_requisition.add_line(self, requisition_id,
                                      other_line)
        self.requisition = self.requisition_model.browse(self.cr, self.uid, requisition_id)

    def make_common_agreements(self):
        """Create two default agreements.

        We have two agreement for same product but using
        different suppliers

        One supplier has a better price for lower qty the other
        has better price for higher qty

        We also create one requisition with one line of agreement product
        And one line of other product

        """

        cr, uid = self.cr, self.uid
        start_date = self.now + timedelta(days=10)
        start_date = start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date = self.now + timedelta(days=20)
        end_date = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        # Agreement 1
        agr_id = self.agreement_model.create(cr, uid,
                                             {'supplier_id': self.supplier_id,
                                              'product_id': self.product_id,
                                              'start_date': start_date,
                                              'end_date': end_date,
                                              'delay': 5,
                                              'quantity': 2000})

        pl_id = self.agreement_pl_model.create(cr, uid,
                                               {'framework_agreement_id': agr_id,
                                                'currency_id': self.ref('base.EUR')})
        self.agreement_line_model.create(cr, uid,
                                         {'framework_agreement_pricelist_id': pl_id,
                                          'quantity': 0,
                                          'price': 77.0})

        self.agreement_line_model.create(cr, uid,
                                         {'framework_agreement_pricelist_id': pl_id,
                                          'quantity': 1000,
                                          'price': 30.0})

        self.cheap_on_high_agreement = self.agreement_model.browse(cr, uid, agr_id)

        # Agreement 2
        agr_id = self.agreement_model.create(cr, uid,
                                             {'supplier_id': self.ref('base.res_partner_3'),
                                              'product_id': self.product_id,
                                              'start_date': start_date,
                                              'end_date': end_date,
                                              'delay': 5,
                                              'quantity': 1200})

        pl_id = self.agreement_pl_model.create(cr, uid,
                                               {'framework_agreement_id': agr_id,
                                                'currency_id': self.ref('base.EUR')})

        self.agreement_line_model.create(cr, uid,
                                         {'framework_agreement_pricelist_id': pl_id,
                                          'quantity': 0,
                                          'price': 50.0})
        self.agreement_line_model.create(cr, uid,
                                         {'framework_agreement_pricelist_id': pl_id,
                                          'quantity': 1000,
                                          'price': 45.0})
        self.cheap_on_low_agreement = self.agreement_model.browse(cr, uid, agr_id)
