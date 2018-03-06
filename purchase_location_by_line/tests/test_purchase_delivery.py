# © 2016 Eficent Business and IT Consulting Services S.L.
#   (<http://www.eficent.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
import time


class TestDeliverySingle(TransactionCase):

    def setUp(self):
        super(TestDeliverySingle, self).setUp()
        # Products
        p1 = self.env.ref('product.product_product_13')
        p2 = self.env.ref('product.product_product_25')

        # Locations
        self.l1 = self.env.ref('stock.stock_location_stock')
        self.l2 = self.env['stock.location'].create({
            'location_id': self.l1.id,
            'name': 'Shelf 1',
            'usage': 'internal'
        })

        # 2 dates we can use to test the features
        self.date_sooner = time.strftime('%Y') + '-01-01'
        self.date_later = time.strftime('%Y') + '-12-31'

        self.po = self.env['purchase.order'].create({
            'partner_id': self.ref('base.res_partner_3'),
            'order_line': [
                (0, 0, {'product_id': p1.id,
                        'product_uom': p1.uom_id.id,
                        'name': p1.name,
                        'price_unit': p1.standard_price,
                        'date_planned': self.date_sooner,
                        'product_qty': 42.0,
                        'location_dest_id': self.l1.id}),
                (0, 0, {'product_id': p2.id,
                        'product_uom': p1.uom_id.id,
                        'name': p2.name,
                        'price_unit': p2.standard_price,
                        'date_planned': self.date_sooner,
                        'product_qty': 12.0,
                        'location_dest_id': self.l1.id}),
                (0, 0, {'product_id': p1.id,
                        'product_uom': p1.uom_id.id,
                        'name': p1.name,
                        'price_unit': p1.standard_price,
                        'date_planned': self.date_sooner,
                        'product_qty': 1.0,
                        'location_dest_id': self.l1.id})]})

    def test_check_single_date(self):
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
        # Change the date of the first line
        self.po.order_line[0].date_planned = self.date_later

        self.assertEquals(
            len(self.po.picking_ids), 0,
            "There must not be pickings for the PO when draft")

        self.po.button_confirm()

        len_pickings = len(self.po.picking_ids)
        self.assertEquals(
            len_pickings, 2,
            "There must be 2 pickings for the PO when confirmed. %s found"
            % len_pickings)

        sorted_pickings = sorted(
            self.po.picking_ids, key=lambda x: x.scheduled_date)
        self.assertEquals(
            sorted_pickings[0].scheduled_date[:10], self.date_sooner,
            "The first picking must be planned at the soonest date")
        self.assertEquals(
            sorted_pickings[1].scheduled_date[:10], self.date_later,
            "The second picking must be planned at the latest date")

        l2_picking = self.po.picking_ids.filtered(
            lambda p: p.location_dest_id == self.l2)
        self.assertEquals(len(l2_picking), 0, 'There must be 0 picking for '
                                              'location Shelf 1')
        l1_picking = self.po.picking_ids.filtered(
            lambda p: p.location_dest_id == self.l1)
        self.assertEquals(len(l1_picking), 2, 'There must be 2 pickings for '
                                              'location Stock')

    def test_check_multiple_locations_same_date(self):
        # Change the location of the first line
        self.po.order_line[0].location_dest_id = self.l2

        self.assertEquals(
            len(self.po.picking_ids), 0,
            "There must not be pickings for the PO when draft")

        self.po.button_confirm()

        l2_picking = self.po.picking_ids.filtered(
            lambda p: p.location_dest_id == self.l2)
        self.assertGreaterEqual(len(l2_picking), 1,
                                'There must be 1 or more '
                                'pickings for location Shelf 1')
        l1_picking = self.po.picking_ids.filtered(
            lambda p: p.location_dest_id == self.l1)
        self.assertGreaterEqual(len(l1_picking), 1, 'There must be 1 or more '
                                                    'pickings for '
                                                    'location Stock')

    def test_check_multiple_locations_multiple_dates(self):
        # Change the location of the first line and date of the second line
        self.po.order_line[0].location_dest_id = self.l2
        self.po.order_line[1].date_planned = self.date_later

        self.assertEquals(
            len(self.po.picking_ids), 0,
            "There must not be pickings for the PO when draft")

        self.po.button_confirm()

        l2_picking = self.po.picking_ids.filtered(
            lambda p: p.location_dest_id == self.l2)
        self.assertGreaterEqual(len(l2_picking), 1,
                                'There must be 1 picking for location Shelf 1')
        l1_picking = self.po.picking_ids.filtered(
            lambda p: p.location_dest_id == self.l1)
        self.assertGreaterEqual(len(l1_picking), 2,
                                'There must be 2 or more '
                                'pickings for location Stock')

        sorted_pickings = sorted(
            self.po.picking_ids, key=lambda x: x.scheduled_date)
        self.assertEquals(
            sorted_pickings[0].scheduled_date[:10], self.date_sooner,
            "The first picking must be planned at the soonest date")
        self.assertEquals(
            sorted_pickings[2].scheduled_date[:10], self.date_later,
            "The second picking must be planned at the latest date")

    def test_check_multiple_locations_multiple_dates_02(self):
        # Leave some locations in the PO line empty
        self.po.order_line[0].location_dest_id = self.l2
        self.po.order_line[1].location_dest_id = False
        self.po.order_line[2].location_dest_id = False
        self.po.order_line[1].date_planned = self.date_later

        self.assertEquals(
            len(self.po.picking_ids), 0,
            "There must not be pickings for the PO when draft")

        self.po.button_confirm()

        l2_picking = self.po.picking_ids.filtered(
            lambda p: p.location_dest_id == self.l2)
        self.assertGreaterEqual(len(l2_picking), 1,
                                'There must be 1 picking for location Shelf 1')
        default_location_picking = self.po.picking_ids.filtered(
            lambda p: p.location_dest_id ==
            self.po.picking_type_id.default_location_dest_id)
        self.assertGreaterEqual(len(default_location_picking), 2,
                                'There must be 2 or more '
                                'pickings for the default location of the PO')

        sorted_pickings = sorted(
            self.po.picking_ids, key=lambda x: x.scheduled_date)
        self.assertEquals(
            sorted_pickings[0].scheduled_date[:10], self.date_sooner,
            "The first picking must be planned at the soonest date")
        self.assertEquals(
            sorted_pickings[2].scheduled_date[:10], self.date_later,
            "The second picking must be planned at the latest date")
