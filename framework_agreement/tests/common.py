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

from openerp.tests import common
from openerp import fields


class AgreementTransactionCase(common.TransactionCase):
    def setUp(self):
        super(AgreementTransactionCase, self).setUp()
        self.Portfolio = self.env['framework.agreement.portfolio']
        self.product = self.env['product.product'].create({
            'name': 'test_1',
            'type': 'product',
            'list_price': 10.00
        })
        self.supplier = self.env.ref('base.res_partner_1')
        start_date = date.today() - timedelta(days=10)

        self.portfolio = self.Portfolio.create({
            'name': '/',
            'supplier_id': self.supplier.id,
            'start_date': fields.Date.to_string(start_date),
        })
        self.portfolio.create_new_agreement()
        self.agreement = self.portfolio.pricelist_ids
