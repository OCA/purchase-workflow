# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class RecommendationCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(RecommendationCase, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Mr. Odoo',
        })
        cls.product_obj = cls.env['product.product']
        cls.prod_1 = cls.product_obj.create({
            'name': 'Test Product 1',
            'type': 'product',
            'seller_ids': [(0, 0, {'name': cls.partner.id, 'price': 5})],
        })
        cls.prod_2 = cls.prod_1.copy({
            'name': 'Test Product 2',
            'seller_ids': [(0, 0, {'name': cls.partner.id, 'price': 10})],
        })
        cls.prod_3 = cls.prod_1.copy({
            'name': 'Test Product 3',
            'seller_ids': [(0, 0, {'name': cls.partner.id, 'price': 7})],
        })
        # Locations
        location_obj = cls.env['stock.location']
        cls.internal_loc = location_obj.create({
            'name': 'Test internal location',
            'usage': 'internal',
        })
        cls.supplier_loc = location_obj.create({
            'name': 'Test supplier location',
            'usage': 'supplier',
        })
        cls.customer_loc = location_obj.create({
            'name': 'Test customer location',
            'usage': 'customer',
        })
        # Create delivered and received lines to have a history
        cls.move_line = cls.env['stock.move.line']
        cls.move_line |= cls.move_line.create({
            'product_id': cls.prod_1.id,
            'product_uom_id': cls.prod_1.uom_id.id,
            'qty_done': 1,
            'date': '2018-01-11 15:05:00',
            'location_id': cls.internal_loc.id,
            'location_dest_id': cls.customer_loc.id,
        })
        cls.move_line |= cls.move_line.create({
            'product_id': cls.prod_2.id,
            'product_uom_id': cls.prod_2.uom_id.id,
            'qty_done': 38,
            'date': '2019-02-01 00:05:00',
            'location_id': cls.internal_loc.id,
            'location_dest_id': cls.customer_loc.id,
        })
        cls.move_line |= cls.move_line.create({
            'product_id': cls.prod_2.id,
            'product_uom_id': cls.prod_2.uom_id.id,
            'qty_done': 4,
            'date': '2019-02-01 00:05:00',
            'location_id': cls.internal_loc.id,
            'location_dest_id': cls.customer_loc.id,
        })
        cls.move_line |= cls.move_line.create({
            'product_id': cls.prod_3.id,
            'product_uom_id': cls.prod_3.uom_id.id,
            'qty_done': 13,
            'date': '2019-02-01 00:06:00',
            'location_id': cls.internal_loc.id,
            'location_dest_id': cls.customer_loc.id,
        })
        cls.move_line |= cls.move_line.create({
            'product_id': cls.prod_3.id,
            'product_uom_id': cls.prod_3.uom_id.id,
            'qty_done': 7,
            'date': '2019-02-01 00:00:00',
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.internal_loc.id,
        })
        cls.move_line.write({
            'state': 'done',
        })
        # Create a purchase order for the same customer
        cls.new_po = cls.env["purchase.order"].create({
            "partner_id": cls.partner.id,
        })

    def wizard(self):
        """Get a wizard."""
        wizard = self.env["purchase.order.recommendation"].with_context(
            active_id=self.new_po.id, active_model='purchase.order'
        ).create({})
        wizard._generate_recommendations()
        return wizard

    def test_recommendations(self):
        """Recommendations are OK."""
        wizard = self.wizard()
        # Order came in from context
        self.assertEqual(wizard.order_id, self.new_po)
        # All our moves are in the past
        self.assertFalse(wizard.line_ids)
        wizard.date_begin = wizard.date_end = '2019-02-01'
        wizard._generate_recommendations()
        self.assertEqual(wizard.line_ids[0].times_delivered, 2)
        self.assertEqual(wizard.line_ids[0].units_delivered, 42)
        self.assertEqual(wizard.line_ids[0].units_included, 42)
        self.assertEqual(wizard.line_ids[0].product_id, self.prod_2)
        self.assertEqual(wizard.line_ids[1].times_delivered, 1)
        self.assertEqual(wizard.line_ids[1].units_delivered, 13)
        self.assertEqual(wizard.line_ids[1].units_included, 13)
        self.assertEqual(wizard.line_ids[1].product_id, self.prod_3)
        # Only 1 product if limited as such
        wizard.line_amount = 1
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 1)
