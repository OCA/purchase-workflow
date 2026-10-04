# Copyright 2023 Tecnativa - Carlos Dauden
# Copyright 2023 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import logging

from odoo.tests import Form, TransactionCase

_logger = logging.getLogger(__name__)


class TestPurchaseStockSecondaryUnit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Active multiple units of measure security group for user
        cls.env.user.groups_id = [(4, cls.env.ref("uom.group_uom").id)]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.ProductSecondaryUnit = cls.env["product.secondary.unit"]
        cls.mto_route = cls.env.ref("stock.route_warehouse0_mto")
        cls.mto_route.active = True
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        cls.supplier = cls.env["res.partner"].create({"name": "test - supplier"})
        with Form(cls.env["product.product"]) as product_form:
            product_form.name = "Test"
            product_form.type = "consu"
            product_form.is_storable = True
            with product_form.secondary_uom_ids.new() as secondary_uom:
                secondary_uom.name = "box"
                secondary_uom.uom_id = cls.product_uom_unit
                secondary_uom.factor = 5.0
        cls.product = product_form.save()
        cls.supplierinfo = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.supplier.id,
                "product_id": cls.product.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )
        cls.product.route_ids = [(6, 0, (cls.mto_route + cls.buy_route).ids)]
        cls.secondary_product_uom = cls.product.secondary_uom_ids[:1]
        cls.sale_order = cls.env["sale.order"]
        with Form(cls.sale_order) as so_form:
            so_form.partner_id = cls.partner
            with so_form.order_line.new() as line:
                line.product_id = cls.product
                line.secondary_uom_id = cls.secondary_product_uom
                line.secondary_uom_qty = 2.0
        cls.sale_order = so_form.save()

    def test_sale_order_propagate_secondary_uom(self):
        # self.sale_order.order_line[0].route_id = self.buy_route
        self.sale_order.action_confirm()
        purchase_order = self.sale_order._get_purchase_orders()
        self.assertEqual(
            purchase_order.order_line[0].secondary_uom_id,
            self.product.secondary_uom_ids[0],
        )
        self.assertEqual(purchase_order.order_line[0].secondary_uom_qty, 2.0)

    def test_sale_order_propagate_secondary_uom_multi_step_buy(self):
        """A 2-step reception route procures an intermediate move (vendor to
        input) that has no sale_line_id of its own - only the delivery move,
        further down its move_dest_ids chain, is linked to the sale order
        line. The secondary unit must still reach the purchase order line in
        that case.
        """
        self.warehouse.reception_steps = "two_steps"
        with Form(self.env["product.product"]) as product_form:
            product_form.name = "Test multi-step"
            product_form.type = "consu"
            product_form.is_storable = True
            with product_form.secondary_uom_ids.new() as secondary_uom:
                secondary_uom.name = "box"
                secondary_uom.uom_id = self.product_uom_unit
                secondary_uom.factor = 5.0
        product = product_form.save()
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
            }
        )
        product.route_ids = [(6, 0, (self.mto_route + self.buy_route).ids)]
        secondary_product_uom = product.secondary_uom_ids[:1]
        with Form(self.env["sale.order"]) as so_form:
            so_form.partner_id = self.partner
            with so_form.order_line.new() as line:
                line.product_id = product
                line.secondary_uom_id = secondary_product_uom
                line.secondary_uom_qty = 2.0
        sale_order = so_form.save()
        sale_order.action_confirm()
        purchase_order = sale_order._get_purchase_orders()
        self.assertEqual(
            purchase_order.order_line[0].secondary_uom_id, secondary_product_uom
        )
        self.assertEqual(purchase_order.order_line[0].secondary_uom_qty, 2.0)
