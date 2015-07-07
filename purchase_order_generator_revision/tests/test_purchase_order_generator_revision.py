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
from openerp.exceptions import ValidationError
from datetime import datetime


class TestPurchaseOrderGenerator(TransactionCase):

    def setUp(self):
        super(TestPurchaseOrderGenerator, self).setUp()

        self.ProductObj = self.env['product.product']
        self.PartnerObj = self.env['res.partner']
        self.LocationObj = self.env['stock.location']
        self.POGeneratorConfigurationObj = self.env[
            'purchase.order.generator.configuration']
        self.POGeneratorConfigurationLineObj = self.env[
            'purchase.order.generator.configuration.line']
        self.POGeneratorObj = self.env['purchase.order.generator']
        self.PurchaseOrderObj = self.env['purchase.order']
        self.POGeneratorRevisionObj = self.env[
            'purchase.order.generator.revision']

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

        self.POGenerator = self.POGeneratorObj.create({
            'date': datetime.today(),
            'configurator_id': self.configurator.id,
            'partner_id': self.partner.id,
            'initial_quantity': 1000,
            'destination_location_id': self.location.id,
        })
        self.POGenerator.validate()

        self.PO = self.PurchaseOrderObj.search(
            [('configurator_id', '=', self.configurator.id)]
        )

        self.revision = self.POGeneratorRevisionObj.create({
            'order_id': self.PO.id,
            'effective_date': datetime.today(),
            'new_target': 5000,
            'revision_factor': 0.95,
            'description': 'Test',
        })

    def test_compute_target_received_qty(self):
        self.assertEqual(
            self.revision.target,
            sum(l.product_qty for l in self.revision.order_id.order_line) *
            sum(l.quantity_ratio for l in
                self.revision.configurator_id.line_ids)
        )

        self.assertEqual(
            self.revision.received_qty,
            sum(
                sum(l.product_uom_qty for l in p.move_lines)
                for p in self.revision.order_id.picking_ids
                if p.state == "done"
            )
        )

    def test_onchange_revision_factor(self):
        self.revision.write({
            'revision_factor': 0.5,
        })
        self.revision._onchange_revision_factor()
        self.assertEqual(
            self.revision.new_target,
            self.revision.target * self.revision.revision_factor
        )

    def test_onchange_new_target(self):
        self.revision.write({
            'new_target': 6000,
        })
        self.revision._onchange_new_target()
        self.assertEqual(
            self.revision.revision_factor,
            self.revision.new_target / self.revision.target
        )

    def test_validate(self):
        self.revision.validate()
