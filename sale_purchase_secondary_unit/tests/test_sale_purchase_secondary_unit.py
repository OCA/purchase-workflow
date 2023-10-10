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
            product_form.detailed_type = "product"
            with product_form.secondary_uom_ids.new() as secondary_uom:
                secondary_uom.name = "box"
                secondary_uom.uom_id = cls.product_uom_unit
                secondary_uom.factor = 5.0
        cls.product = product_form.save()
        cls.supplierinfo = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
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
