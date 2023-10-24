# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# Copyright 2020 Manuel Calero - Tecnativa
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class RecommendationCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.category_obj = cls.env["product.category"]
        cls.categ1 = cls.category_obj.create({"name": "Test Cat 1"})
        cls.categ2 = cls.category_obj.create({"name": "Test Cat 2"})
        cls.product_obj = cls.env["product.product"]
        cls.prod_1 = cls.product_obj.create(
            {
                "default_code": "product-1",
                "name": "Test Product 1",
                "categ_id": cls.categ1.id,
                "type": "product",
                "seller_ids": [(0, 0, {"partner_id": cls.partner.id, "price": 5})],
            }
        )
        cls.prod_2 = cls.product_obj.create(
            {
                "default_code": "product-2",
                "name": "Test Product 2",
                "categ_id": cls.categ2.id,
                "type": "product",
                "seller_ids": [(0, 0, {"partner_id": cls.partner.id, "price": 10})],
            }
        )
        cls.prod_3 = cls.product_obj.create(
            {
                "default_code": "product-3",
                "name": "Test Product 3",
                "categ_id": cls.categ2.id,
                "type": "product",
                "seller_ids": [(0, 0, {"partner_id": cls.partner.id, "price": 7})],
            }
        )
        # Warehouses
        cls.wh1 = cls.env["stock.warehouse"].create(
            {"name": "TEST WH1", "code": "TST1"}
        )
        cls.wh2 = cls.env["stock.warehouse"].create(
            {"name": "TEST WH2", "code": "TST2"}
        )
        # Locations
        location_obj = cls.env["stock.location"]
        cls.supplier_loc = location_obj.create(
            {"name": "Test supplier location", "usage": "supplier"}
        )
        cls.customer_loc = location_obj.create(
            {"name": "Test customer location", "usage": "customer"}
        )
        # Create deliveries and receipts orders to have a history
        cls.picking_obj = cls.env["stock.picking"]
        cls.picking_1 = cls.picking_obj.create(
            {
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "partner_id": cls.partner.id,
                "picking_type_id": cls.wh1.out_type_id.id,
            }
        )
        cls.picking_2 = cls.picking_obj.create(
            {
                "location_id": cls.wh2.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "partner_id": cls.partner.id,
                "picking_type_id": cls.wh2.out_type_id.id,
            }
        )
        cls.picking_3 = cls.picking_obj.create(
            {
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "partner_id": cls.partner.id,
                "picking_type_id": cls.wh1.in_type_id.id,
            }
        )
        cls.move_line = cls.env["stock.move.line"]
        cls.move_line |= cls.move_line.create(
            {
                "product_id": cls.prod_1.id,
                "product_uom_id": cls.prod_1.uom_id.id,
                "qty_done": 1,
                "date": fields.Datetime.from_string("2018-01-11 15:05:00"),
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "picking_id": cls.picking_1.id,
            }
        )
        cls.move_line |= cls.move_line.create(
            {
                "product_id": cls.prod_2.id,
                "product_uom_id": cls.prod_2.uom_id.id,
                "qty_done": 38,
                "date": fields.Datetime.from_string("2019-02-01 00:05:00"),
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "picking_id": cls.picking_1.id,
            }
        )
        cls.move_line |= cls.move_line.create(
            {
                "product_id": cls.prod_2.id,
                "product_uom_id": cls.prod_2.uom_id.id,
                "qty_done": 4,
                "date": fields.Datetime.from_string("2019-02-01 00:05:00"),
                "location_id": cls.wh2.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "picking_id": cls.picking_2.id,
            }
        )
        cls.move_line |= cls.move_line.create(
            {
                "product_id": cls.prod_3.id,
                "product_uom_id": cls.prod_3.uom_id.id,
                "qty_done": 13,
                "date": fields.Datetime.from_string("2019-02-01 00:06:00"),
                "location_id": cls.wh2.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "picking_id": cls.picking_2.id,
            }
        )
        cls.move_line |= cls.move_line.create(
            {
                "product_id": cls.prod_3.id,
                "product_uom_id": cls.prod_3.uom_id.id,
                "qty_done": 7,
                "date": fields.Datetime.from_string("2019-02-01 00:00:00"),
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "picking_id": cls.picking_3.id,
            }
        )
        cls.move_line.write({"state": "done"})
        # Total stock available for prod3 is 5 units split in two warehouses
        quant_obj = cls.env["stock.quant"]
        quant_obj.create(
            {
                "product_id": cls.prod_3.id,
                "location_id": cls.wh1.lot_stock_id.id,
                "quantity": 2.0,
            }
        )
        quant_obj.create(
            {
                "product_id": cls.prod_3.id,
                "location_id": cls.wh2.lot_stock_id.id,
                "quantity": 3.0,
            }
        )
        # Create a purchase order for the same customer
        cls.new_po = cls.env["purchase.order"].create({"partner_id": cls.partner.id})

    def wizard(self):
        """Get a wizard."""
        wizard = (
            self.env["purchase.order.recommendation"]
            .with_context(active_id=self.new_po.id, active_model="purchase.order")
            .create({})
        )
        wizard._generate_recommendations()
        return wizard


class RecommendationCaseTests(RecommendationCase):
    def test_recommendations(self):
        """Recommendations are OK."""
        wizard = self.wizard()
        # Order came in from context
        self.assertEqual(wizard.order_id, self.new_po)
        # All our moves are in the past
        self.assertFalse(wizard.line_ids)
        wizard.date_begin = wizard.date_end = fields.Date.from_string("2019-02-01")
        wizard._generate_recommendations()
        line_prod_2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertEqual(line_prod_2.times_delivered, 2)
        self.assertEqual(line_prod_2.units_delivered, 42)
        self.assertEqual(line_prod_2.units_included, 42)
        line_prod_3 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_3)
        self.assertEqual(line_prod_3.times_delivered, 1)
        self.assertEqual(line_prod_3.units_delivered, 13)
        self.assertEqual(line_prod_3.units_included, 8)
        self.assertEqual(line_prod_3.units_available, 5)
        self.assertEqual(line_prod_3.units_virtual_available, 5)
        # Only 1 product if limited as such
        wizard.line_amount = 1
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 1)

    def test_recommendations_by_warehouse(self):
        """We can split recommendations by delivery warehouse"""
        wizard = self.wizard()
        wizard.date_begin = wizard.date_end = fields.Date.from_string("2019-02-01")
        # Just delivered to WH2
        wizard.warehouse_ids = self.wh2
        wizard._generate_recommendations()
        line_prod_2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertEqual(line_prod_2.times_delivered, 1)
        self.assertEqual(line_prod_2.units_delivered, 4)
        self.assertEqual(line_prod_2.units_included, 4)
        line_prod_3 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_3)
        self.assertEqual(line_prod_3.times_delivered, 1)
        self.assertEqual(line_prod_3.units_delivered, 13)
        self.assertEqual(line_prod_3.units_included, 10)
        self.assertEqual(line_prod_3.units_available, 3)
        self.assertEqual(line_prod_3.units_virtual_available, 3)
        # Just delivered to WH1
        wizard.warehouse_ids = self.wh1
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 2)
        line_prod_2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertEqual(line_prod_2.times_delivered, 1)
        self.assertEqual(line_prod_2.units_delivered, 38)
        self.assertEqual(line_prod_2.units_included, 38)
        line_prod_3 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_3)
        self.assertEqual(line_prod_3.times_delivered, 0)
        self.assertEqual(line_prod_3.units_delivered, 0)
        self.assertEqual(line_prod_3.units_received, 7)
        self.assertEqual(line_prod_3.units_included, 0)
        self.assertEqual(line_prod_3.units_available, 2)
        self.assertEqual(line_prod_3.units_virtual_available, 2)
        # Delivered to both warehouses
        wizard.warehouse_ids |= self.wh2
        wizard._generate_recommendations()
        line_prod_2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertEqual(line_prod_2.times_delivered, 2)
        self.assertEqual(line_prod_2.units_delivered, 42)
        self.assertEqual(line_prod_2.units_included, 42)
        line_prod_3 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_3)
        self.assertEqual(line_prod_3.times_delivered, 1)
        self.assertEqual(line_prod_3.units_delivered, 13)
        self.assertEqual(line_prod_3.units_included, 8)
        self.assertEqual(line_prod_3.units_available, 5)
        self.assertEqual(line_prod_3.units_virtual_available, 5)

    def test_action_accept(self):
        """Open wizard when there are PO Lines and click on Accept"""
        po_line = self.env["purchase.order.line"].new(
            {"sequence": 1, "order_id": self.new_po.id, "product_id": self.prod_2.id}
        )
        po_line.onchange_product_id()
        po_line.product_qty = 10
        self.new_po.order_line = po_line
        # Create wizard and set dates
        wizard = self.wizard()
        wizard.date_begin = wizard.date_end = fields.Date.from_string("2019-02-01")
        wizard._generate_recommendations()
        # After change dates, in the recommendation line corresponding to the
        # self.prod_2 Units Included must be 10
        line_prod_2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertEqual(line_prod_2.units_included, 10)
        line_prod_3 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_3)
        self.assertEqual(line_prod_3.units_included, 8)
        # Change Units Included amount to 20 and accept, then the product_qty
        # of the PO Line corresponding to the self.prod_2 must change to 20
        line_prod_2.units_included = 20
        wizard.action_accept()
        self.assertEqual(len(self.new_po.order_line), 2)
        po_line_prod_2 = self.new_po.order_line.filtered(
            lambda x: x.product_id == self.prod_2
        )
        self.assertEqual(po_line_prod_2.product_qty, 20)
        po_line_prod_3 = self.new_po.order_line.filtered(
            lambda x: x.product_id == self.prod_3
        )
        self.assertEqual(po_line_prod_3.product_qty, 8)

    def test_recommendations_by_category(self):
        """We can split recommendations by delivery warehouse"""
        wizard = self.wizard()
        wizard.date_begin = wizard.date_end = fields.Date.from_string(
            "2019-02-01"
        )  # "2019-02-01"
        # Just delivered from category 1
        wizard.product_category_ids = self.categ1
        wizard.show_all_partner_products = True
        wizard._generate_recommendations()
        # Just one line with products from category 1
        self.assertEqual(wizard.line_ids.product_id, self.prod_1)
        # Just delivered from category 2
        wizard.product_category_ids = self.categ2
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 2)
        # All categorys
        wizard.product_category_ids += self.categ1
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 3)
        # No category set
        wizard.product_category_ids = False
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 3)
        # All products
        wizard.show_all_products = True
        wizard.line_amount = 0
        wizard._generate_recommendations()
        purchase_products_number = self.product_obj.search_count(
            [("purchase_ok", "!=", False)]
        )
        self.assertEqual(len(wizard.line_ids), purchase_products_number)

    def test_recommendations_inactive_product(self):
        """Recommendations are OK."""
        self.prod_2.active = False
        wizard = self.wizard()
        wizard.date_begin = wizard.date_end = fields.Date.from_string("2019-02-01")
        wizard._generate_recommendations()
        # The first recommendation line is the prod_3, as prod_2 is archived
        self.assertEqual(wizard.line_ids[0].product_id, self.prod_3)
        self.prod_3.purchase_ok = False
        wizard._generate_recommendations()
        # No recommendations as both elegible products are excluded
        self.assertFalse(wizard.line_ids)
