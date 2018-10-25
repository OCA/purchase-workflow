# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestDeliverySingle(TransactionCase):

    def setUp(self):
        super(TestDeliverySingle, self).setUp()
        self.product_model = self.env['product.product']

        # Create products:
        p1 = self.product1 = self.product_model.create({
            'name': 'Test Product 1',
            'type': 'product',
            'default_code': 'PROD1',
        })
        p2 = self.product2 = self.product_model.create({
            'name': 'Test Product 2',
            'type': 'product',
            'default_code': 'PROD2',
        })

        # Two dates which we can use to test the features:
        self.date_sooner = '2015-01-01'
        self.date_later = '2015-12-13'

        self.po = self.env['purchase.order'].create({
            'partner_id': self.ref('base.res_partner_3'),
            'order_line': [
                (0, 0, {'product_id': p1.id,
                        'product_uom': p1.uom_id.id,
                        'name': p1.name,
                        'price_unit': p1.standard_price,
                        'date_planned': self.date_sooner,
                        'product_qty': 42.0}),
                (0, 0, {'product_id': p2.id,
                        'product_uom': p2.uom_id.id,
                        'name': p2.name,
                        'price_unit': p2.standard_price,
                        'date_planned': self.date_sooner,
                        'product_qty': 12.0}),
                (0, 0, {'product_id': p1.id,
                        'product_uom': p1.uom_id.id,
                        'name': p1.name,
                        'price_unit': p1.standard_price,
                        'date_planned': self.date_sooner,
                        'product_qty': 1.0})]})

    def test_check_single_date(self):
        """Tests with single date."""
        self.assertEquals(
            len(self.po.picking_ids), 0,
            "There must not be pickings for the PO when draft")
        self.po.button_confirm()
        self.assertEquals(
            len(self.po.picking_ids), 1,
            "There must be 1 picking for the PO when confirmed")
        self.assertEquals(
            self.po.picking_ids[0].scheduled_date[:10], self.date_sooner,
            "The picking must be planned at the expected date")

    def test_check_multiple_dates(self):
        """Tests changing the date of the first line."""
        self.po.order_line[0].date_planned = self.date_later
        self.assertEquals(
            len(self.po.picking_ids), 0,
            "There must not be pickings for the PO when draft")
        self.po.button_confirm()
        self.assertEquals(
            len(self.po.picking_ids), 2,
            "There must be 2 pickings for the PO when confirmed. %s found"
            % len(self.po.picking_ids))

        sorted_pickings = sorted(
            self.po.picking_ids, key=lambda x: x.scheduled_date)
        self.assertEquals(
            sorted_pickings[0].scheduled_date[:10], self.date_sooner,
            "The first picking must be planned at the soonest date")
        self.assertEquals(
            sorted_pickings[1].scheduled_date[:10], self.date_later,
            "The second picking must be planned at the latest date")
