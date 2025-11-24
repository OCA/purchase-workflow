# Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestPurchaseComputeOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_3 = cls.env.ref("base.res_partner_3")
        cls.cmp_purchase_order = cls.env["computed.purchase.order"].create(
            {
                "partner_id": cls.partner_3.id,
                "purchase_target": 20,
                "target_type": "time",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "standard_price": 10,
                "list_price": 15,
                "purchase_ok": True,
                "is_storable": True,
                "consumption_calculation_method": "moves",
                "calculation_range": 10,
            }
        )
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.partner_3.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "min_qty": 1,
                "price": 10,
            }
        )
        picking_form = Form(cls.env["stock.picking"])
        picking_form.partner_id = cls.partner_3
        picking_form.picking_type_id = cls.env.ref("stock.picking_type_in")
        cls.picking = picking_form.save()
        cls.move = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking.id,
                "product_id": cls.product.id,
                "name": "Test",
                "product_uom_qty": 20,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "quantity": 20,
                "location_id": cls.picking.location_id.id,
                "location_dest_id": cls.picking.location_dest_id.id,
            }
        )
        cls.move.picked = True
        cls.picking._action_done()
        cls.cmp_purchase_order.compute_active_product_stock()
        cls.cmp_po_line = cls.cmp_purchase_order.line_ids.filtered(
            lambda line: line.product_id.id == cls.product.id
        )

    def test_001_get_product_and_stock(self):
        self.assertEqual(
            self.cmp_po_line.qty_available,
            20.0,
            "Available Quantity of a product should be 20.0",
        )

    def test_002_compute_purchase_quantities(self):
        # Purchase Quantity Calculation:
        # purchase_qty = purchase_target x average_consumption - \
        # (qty_available + incoming_qty - outgoing_qty)
        self.cmp_po_line.average_consumption = 15
        self.cmp_purchase_order.compute_purchase_quantities()
        self.assertEqual(
            self.cmp_po_line.purchase_qty,
            280.0,
            "Purchase Quantity of a product should be 60.0",
        )

    def test_003_make_purchase_order(self):
        self.cmp_po_line.average_consumption = 15
        self.cmp_purchase_order.compute_purchase_quantities()
        self.cmp_purchase_order.make_order()
        po_line = self.cmp_purchase_order.purchase_order_id.order_line.filtered(
            lambda line: line.product_id.id == self.product.id
        )
        self.assertEqual(
            po_line.product_qty,
            self.cmp_po_line.purchase_qty,
            "Purchase Quantity of a product should be "
            f"{self.cmp_po_line.purchase_qty}",
        )
