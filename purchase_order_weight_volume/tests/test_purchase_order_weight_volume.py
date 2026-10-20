# Copyright 2023 Camptocamp
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
import time

from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestPurchaseOrderWeightVolume(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.po_obj = cls.env["purchase.order"]
        cls.company_obj = cls.env["res.company"]

        # Company
        cls._prepare_company()

        # Partner
        cls._prepare_partner()

        # Product
        cls._prepare_product()

        # Lines of Purchase Order
        cls._prepare_line_products()

        # UoM
        cls._prepare_uom()

    @classmethod
    def _prepare_company(cls):
        cls.company1 = cls.company_obj.create(
            {
                "name": "Company 1",
                "display_order_weight_in_po": True,
                "display_order_volume_in_po": True,
            }
        )

    @classmethod
    def _prepare_partner(cls):
        cls.partner1 = cls.env.ref("base.res_partner_12")

    @classmethod
    def _prepare_product(cls):
        cls.product1 = cls.env.ref("product.product_product_6")
        cls.product1.write(
            {
                "weight": 5,
                "volume": 50,
            }
        )

        cls.product2 = cls.env.ref("product.product_product_7")
        cls.product2.write(
            {
                "weight": 0.5,
                "volume": 15,
            }
        )

    @classmethod
    def _prepare_line_products(cls):
        cls.line_products = [
            (cls.product1, 10),
            (cls.product2, 5),
        ]

        cls.total_weight = 0
        cls.total_volume = 0

        for product, qty in cls.line_products:
            cls.total_weight += product.weight * qty
            cls.total_volume += product.volume * qty

    @classmethod
    def _prepare_uom(cls):
        # Configure weight in kg
        cls.product_uom_kgm = cls.env.ref("uom.product_uom_kgm")
        cls.env["ir.config_parameter"].sudo().set_param(
            "product_default_weight_uom_id", cls.product_uom_kgm.id
        )

        # Configure volume in m3
        cls.product_uom_cubic_meter = cls.env.ref("uom.product_uom_cubic_meter")
        cls.env["ir.config_parameter"].sudo().set_param(
            "product_default_volume_uom_id", cls.product_uom_cubic_meter.id
        )

    def test_purchase_order_weight_volume(self):
        po = self._create_purchase(self.line_products)

        # Purchase Order
        self.assertEqual(po.total_weight, self.total_weight)
        self.assertEqual(po.total_weight_uom_id, self.product_uom_kgm)

        self.assertEqual(po.total_volume, self.total_volume)
        self.assertEqual(po.total_volume_uom_id, self.product_uom_cubic_meter)

        # Purchase Order Line
        for line in po.order_line:
            self.assertEqual(
                line.line_weight, line.product_id.weight * line.product_uom_qty
            )
            self.assertEqual(
                line.line_volume, line.product_id.volume * line.product_uom_qty
            )

    def _create_purchase(self, line_products):
        """Create a purchase order.
        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []

        for product, qty in line_products:
            line_values = {
                "name": product.name,
                "product_id": product.id,
                "product_qty": qty,
                "product_uom": product.uom_id.id,
                "price_unit": 100,
                "date_planned": time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            }

            lines.append((0, 0, line_values))

        res = self.po_obj.create(
            {
                "partner_id": self.partner1.id,
                "order_line": lines,
            }
        )

        return res
