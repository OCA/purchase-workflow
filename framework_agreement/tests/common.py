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


class BaseAgreementTestMixin(object):
    """Class that contain common behavior for all agreement unit test classes.

    We use Mixin because we want to have those behaviors on the various
    unit test subclasses provided by OpenERP in test common.

    """

    def commonsetUp(self):
        self.agreement_model = self.env['framework.agreement']
        self.agreement_pl_model = self.env['framework.agreement.pricelist']
        self.agreement_line_model = self.env['framework.agreement.line']
        self.product = self.env['product.product'].create({
            'name': 'test_1',
            'type': 'product',
            'list_price': 10.00
        })
        self.supplier = self.env.ref('base.res_partner_1')
        self.portfolio = self.env['framework.agreement.portfolio'].create({
            'name': '/',
            'supplier_id': self.supplier.id,
        })
