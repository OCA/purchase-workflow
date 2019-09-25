# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.stock_return_request.tests.test_stock_return_request_common\
    import StockReturnRequestCase


class PurchaseReturnRequestCase(StockReturnRequestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # TODO: Declare new supplier
        cls.partner_supplier_2 = cls.env['res.partner'].create({
            'name': 'Mr. Purchase',
            'property_stock_supplier': cls.supplier_loc.id,
            'property_stock_customer': cls.customer_loc.id,
        })
        # TODO: Declare two purchase orders and receive their items
        cls.po_1 = cls.env["purchase.order"].create({
            "partner_id": cls.partner_supplier_2.id,
            'picking_type_id': cls.wh1.in_type_id.id,
            "order_line": [
                (0, False, {
                    "product_id": cls.prod_3.id,
                    "name": cls.prod_3.name,
                    "product_qty": 50.0,
                    "price_unit": 10.0,
                    "product_uom": cls.prod_3.uom_id.id,
                    "date_planned": "2019-10-01",
                }),
            ],
        })
        cls.po_2 = cls.po_1.copy()
        cls.purchase_orders = cls.po_1 | cls.po_2
        # Confirm all the purchase orders
        for order in cls.purchase_orders:
            order.button_confirm()
        # Receive products. For each picking:
        # 10 units of TSTPROD3LOT0001 -> 20 units +90 already existing
        # 40 units of TSTPROD3LOT0002 -> 80 units +10 already existing
        for picking in cls.purchase_orders.mapped('picking_ids'):
            for ml in picking.move_line_ids:
                ml.write({
                    'lot_id': cls.prod_3_lot1.id,
                    'qty_done': 10.0,
                })
                ml.copy({
                    'lot_id': cls.prod_3_lot2.id,
                    'qty_done': 40.0,
                })
            picking.action_done()

    def test_01_return_purchase_stock_to_supplier(self):
        """Return stock to supplier and the corresponding
           purchases are ready for refund"""
        self.return_request_supplier.write({
            'partner_id': self.partner_supplier_2.id,
            'to_refund': True,
            'line_ids': [
                (0, 0, {
                    'product_id': self.prod_3.id,
                    'lot_id': self.prod_3_lot1.id,
                    'quantity': 12.0,
                }),
                (0, 0, {
                    'product_id': self.prod_3.id,
                    'lot_id': self.prod_3_lot2.id,
                    'quantity': 22.0,
                }),
            ],
        })
        self.return_request_supplier.onchange_locations()
        self.return_request_supplier.action_confirm()
        purchase_orders = self.return_request_supplier.purchase_order_ids
        pickings = self.return_request_supplier.returned_picking_ids
        moves = self.return_request_supplier.returned_picking_ids.mapped(
            'move_lines')
        # For lot TSTPROD3LOT0001 we'll be returning:
        # ==>  2 units from PO01
        # ==> 10 units from PO02
        # For lot TSTPROD3LOT0002 we'll be returning:
        # ==> 22 units from PO01
        self.assertEqual(len(purchase_orders), 2)
        self.assertEqual(len(pickings), 2)
        # Two moves with two move lines each
        self.assertEqual(len(moves), 2)
        self.assertAlmostEqual(
            sum(moves.mapped('product_uom_qty')), 34.0)
        # Process the return to validate all the pickings
        self.return_request_supplier.action_validate()
        self.assertTrue(all([
            True if x == 'done' else False for x in pickings.mapped('state')]))
        # For lot TSTPROD3LOT0001 we had 110 units
        prod_3_qty_lot_1 = self.prod_3.with_context(
            location=self.wh1.lot_stock_id.id,
            lot_id=self.prod_3_lot1.id).qty_available
        # For lot TSTPROD3LOT0002 we had 90 units
        prod_3_qty_lot_2 = self.prod_3.with_context(
            location=self.wh1.lot_stock_id.id,
            lot_id=self.prod_3_lot2.id).qty_available
        self.assertAlmostEqual(prod_3_qty_lot_1, 98.0)
        self.assertAlmostEqual(prod_3_qty_lot_2, 68.0)
        # There were 100 units in the purchase orders.
        self.assertAlmostEqual(
            sum(purchase_orders.mapped('order_line.qty_received')), 66.0)
