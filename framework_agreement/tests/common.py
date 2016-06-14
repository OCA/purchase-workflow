# -*- coding: utf-8 -*-
# © 2013-2015 Camptocamp SA - Nicolas Bessi, Leonardo Pistone
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


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
