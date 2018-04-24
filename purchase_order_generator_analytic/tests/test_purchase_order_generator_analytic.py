# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp.tests import TransactionCase
from datetime import datetime


class TestPurchaseOrderGenerator(TransactionCase):

    def setUp(self):
        super(TestPurchaseOrderGenerator, self).setUp()

        self.ProductObj = self.env['product.product']
        self.PartnerObj = self.env['res.partner']
        self.LocationObj = self.env['stock.location']
        self.AnalyticObj = self.env['account.analytic.account']
        self.POGeneratorConfigurationObj = self.env[
            'purchase.order.generator.configuration']
        self.POGeneratorConfigurationLineObj = self.env[
            'purchase.order.generator.configuration.line']
        self.POGeneratorObj = self.env['purchase.order.generator']

        self.configurator = self.POGeneratorConfigurationObj.create({
            'name': 'Test configuration',
            'interval': 2,
            'recurrence_type': 'weekly',
        })

        self.product = self.ProductObj.create({
            'name': 'Egg',
        })

        self.partner = self.PartnerObj.create({
            'name': 'Test supplier',
        })

        self.location = self.LocationObj.create({
            'name': 'Test location',
            'usage': 'internal',
        })

        self.analytic = self.AnalyticObj.create({
            'name': 'Test analytic account',
            'type': 'normal',
        })

        self.POGeneratorConfigurationLineObj.create({
            'configurator_id': self.configurator.id,
            'product_id': self.product.id,
            'quantity_ratio': 0.5,
            'sequence': 1,
        })

        self.POGeneratorConfigurationLineObj.create({
            'configurator_id': self.configurator.id,
            'product_id': self.product.id,
            'quantity_ratio': 1.5,
            'sequence': 2,
        })

        self.POGeneratorConfigurationLineObj.create({
            'configurator_id': self.configurator.id,
            'product_id': self.product.id,
            'quantity_ratio': 3,
            'sequence': 3,
        })

    def test_generator_wizard(self):
        self.POGenerator = self.POGeneratorObj.create({
            'date': datetime.today(),
            'configurator_id': self.configurator.id,
            'partner_id': self.partner.id,
            'initial_quantity': 1000,
            'destination_location_id': self.location.id,
            'analytic_id': self.analytic.id,
        })
        self.POGenerator.validate()
