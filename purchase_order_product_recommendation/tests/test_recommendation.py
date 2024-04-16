# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime
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
        # Warehouses
        cls.wh1 = cls.env['stock.warehouse'].create({
            'name': 'TEST WH1',
            'code': 'TST1',
        })
        cls.wh2 = cls.env['stock.warehouse'].create({
            'name': 'TEST WH2',
            'code': 'TST2',
        })
        # Locations
        location_obj = cls.env['stock.location']
        cls.supplier_loc = location_obj.create({
            'name': 'Test supplier location',
            'usage': 'supplier',
        })
        cls.customer_loc = location_obj.create({
            'name': 'Test customer location',
            'usage': 'customer',
        })
        # Create deliveries and receipts orders to have a history
        cls.picking_obj = cls.env['stock.picking']
        cls.picking_1 = cls.picking_obj.create({
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'partner_id': cls.partner.id,
            'picking_type_id': cls.wh1.out_type_id.id,
        })
        cls.picking_2 = cls.picking_obj.create({
            'location_id': cls.wh2.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'partner_id': cls.partner.id,
            'picking_type_id': cls.wh2.out_type_id.id,
        })
        cls.picking_3 = cls.picking_obj.create({
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.wh1.lot_stock_id.id,
            'partner_id': cls.partner.id,
            'picking_type_id': cls.wh1.in_type_id.id,
        })
        cls.move_line = cls.env['stock.move.line']
        cls.move_line |= cls.move_line.create({
            'product_id': cls.prod_1.id,
            'product_uom_id': cls.prod_1.uom_id.id,
            'qty_done': 1,
            'date': datetime(2018, 1, 11, 15, 5),
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'picking_id': cls.picking_1.id,
        })
        cls.move_line |= cls.move_line.create({
            'product_id': cls.prod_2.id,
            'product_uom_id': cls.prod_2.uom_id.id,
            'qty_done': 38,
            'date': datetime(2019, 2, 1, 0, 5),
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'picking_id': cls.picking_1.id,
        })
        cls.move_line |= cls.move_line.create({
            'product_id': cls.prod_2.id,
            'product_uom_id': cls.prod_2.uom_id.id,
            'qty_done': 4,
            'date': datetime(2019, 2, 1, 0, 5),
            'location_id': cls.wh2.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'picking_id': cls.picking_2.id,
        })
        cls.move_line |= cls.move_line.create({
            'product_id': cls.prod_3.id,
            'product_uom_id': cls.prod_3.uom_id.id,
            'qty_done': 13,
            'date': datetime(2019, 2, 1, 0, 6),
            'location_id': cls.wh2.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'picking_id': cls.picking_2.id,
        })
        cls.move_line |= cls.move_line.create({
            'product_id': cls.prod_3.id,
            'product_uom_id': cls.prod_3.uom_id.id,
            'qty_done': 7,
            'date': datetime(2019, 2, 1, 0, 0),
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.wh1.lot_stock_id.id,
            'picking_id': cls.picking_3.id,
        })
        cls.move_line.write({
            'state': 'done',
        })
        # Total stock available for prod3 is 5 units split in two warehouses
        quant_obj = cls.env['stock.quant']
        quant_obj.create({
            'product_id': cls.prod_3.id,
            'location_id': cls.wh1.lot_stock_id.id,
            'quantity': 2.0,
        })
        quant_obj.create({
            'product_id': cls.prod_3.id,
            'location_id': cls.wh2.lot_stock_id.id,
            'quantity': 3.0,
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
        wizard.date_begin = wizard.date_end = date(2019, 2, 1)
        wizard._generate_recommendations()
        self.assertEqual(wizard.line_ids[0].times_delivered, 2)
        self.assertEqual(wizard.line_ids[0].units_delivered, 42)
        self.assertEqual(wizard.line_ids[0].units_included, 42)
        self.assertEqual(wizard.line_ids[0].product_id, self.prod_2)
        self.assertEqual(wizard.line_ids[1].times_delivered, 1)
        self.assertEqual(wizard.line_ids[1].units_delivered, 13)
        self.assertEqual(wizard.line_ids[1].units_included, 8)
        self.assertEqual(wizard.line_ids[1].product_id, self.prod_3)
        self.assertEqual(wizard.line_ids[1].units_available, 5)
        self.assertEqual(wizard.line_ids[1].units_virtual_available, 5)
        # Only 1 product if limited as such
        wizard.line_amount = 1
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 1)

    def test_recommendations_by_warehouse(self):
        """We can split recommendations by delivery warehouse"""
        wizard = self.wizard()
        wizard.date_begin = wizard.date_end = date(2019, 2, 1)
        # Just delivered to WH2
        wizard.warehouse_ids = self.wh2
        wizard._generate_recommendations()
        self.assertEqual(wizard.line_ids[0].times_delivered, 1)
        self.assertEqual(wizard.line_ids[0].units_delivered, 4)
        self.assertEqual(wizard.line_ids[0].units_included, 4)
        self.assertEqual(wizard.line_ids[0].product_id, self.prod_2)
        self.assertEqual(wizard.line_ids[1].times_delivered, 1)
        self.assertEqual(wizard.line_ids[1].units_delivered, 13)
        self.assertEqual(wizard.line_ids[1].units_included, 10)
        self.assertEqual(wizard.line_ids[1].product_id, self.prod_3)
        self.assertEqual(wizard.line_ids[1].units_available, 3)
        self.assertEqual(wizard.line_ids[1].units_virtual_available, 3)
        # Just delivered to WH1
        wizard.warehouse_ids = self.wh1
        wizard._generate_recommendations()
        self.assertEqual(wizard.line_ids[0].times_delivered, 1)
        self.assertEqual(wizard.line_ids[0].units_delivered, 38)
        self.assertEqual(wizard.line_ids[0].units_included, 38)
        self.assertEqual(wizard.line_ids[0].product_id, self.prod_2)
        self.assertEqual(wizard.line_ids[1].times_delivered, 0)
        self.assertEqual(wizard.line_ids[1].units_delivered, 0)
        self.assertEqual(wizard.line_ids[1].units_received, 7)
        self.assertEqual(wizard.line_ids[1].units_included, 0)
        self.assertEqual(wizard.line_ids[1].product_id, self.prod_3)
        self.assertEqual(len(wizard.line_ids), 2)
        self.assertEqual(wizard.line_ids[1].units_available, 2)
        self.assertEqual(wizard.line_ids[1].units_virtual_available, 2)
        # Delivered to both warehouses
        wizard.warehouse_ids |= self.wh2
        wizard._generate_recommendations()
        self.assertEqual(wizard.line_ids[0].times_delivered, 2)
        self.assertEqual(wizard.line_ids[0].units_delivered, 42)
        self.assertEqual(wizard.line_ids[0].units_included, 42)
        self.assertEqual(wizard.line_ids[0].product_id, self.prod_2)
        self.assertEqual(wizard.line_ids[1].times_delivered, 1)
        self.assertEqual(wizard.line_ids[1].units_delivered, 13)
        self.assertEqual(wizard.line_ids[1].units_included, 8)
        self.assertEqual(wizard.line_ids[1].product_id, self.prod_3)
        self.assertEqual(wizard.line_ids[1].units_available, 5)
        self.assertEqual(wizard.line_ids[1].units_virtual_available, 5)

    def test_action_accept(self):
        """Open wizard when there are no PO Lines and click on Accept"""
        wizard = self.wizard()
        wizard.date_begin = wizard.date_end = date(2019, 2, 1)
        wizard._generate_recommendations()
        wizard.action_accept()
        self.assertEqual(len(self.new_po.order_line), 2)
        self.assertEqual(self.new_po.order_line[0].product_id, self.prod_2)
        self.assertEqual(self.new_po.order_line[0].product_qty, 42)
        self.assertEqual(self.new_po.order_line[1].product_id, self.prod_3)
        self.assertEqual(self.new_po.order_line[1].product_qty, 8)

    def test_action_accept(self):
        """Open wizard when there are PO Lines and click on Accept"""
        # po_line = self.env['purchase.order.line'].create({
        po_line = self.env['purchase.order.line'].new({
            'sequence': 1,
            'order_id': self.new_po.id,
            'product_id': self.prod_2.id,
        })
        po_line.onchange_product_id()
        po_line.product_qty = 10
        po_line._onchange_quantity()
        self.new_po.order_line = po_line
        # Create wizard and set dates
        wizard = self.wizard()
        wizard.date_begin = wizard.date_end = date(2019, 2, 1)
        wizard._generate_recommendations()
        # After change dates, in the recommendation line corresponding to the
        # self.prod_2 Units Included must be 10
        self.assertEqual(wizard.line_ids[0].units_included, 10)
        self.assertEqual(wizard.line_ids[1].units_included, 8)
        # Change Units Included amount to 20 and accept, then the product_qty
        # of the PO Line corresponding to the self.prod_2 must change to 20
        wizard.line_ids[0].units_included = 20
        wizard.action_accept()
        self.assertEqual(len(self.new_po.order_line), 2)
        self.assertEqual(self.new_po.order_line[0].product_id, self.prod_2)
        self.assertEqual(self.new_po.order_line[0].product_qty, 20)
        self.assertEqual(self.new_po.order_line[1].product_id, self.prod_3)
        self.assertEqual(self.new_po.order_line[1].product_qty, 8)
