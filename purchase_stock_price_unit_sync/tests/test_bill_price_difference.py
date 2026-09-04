# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import unittest

from odoo import Command, fields

from odoo.addons.base.tests.common import BaseCommon


class TestBillPriceDifference(BaseCommon):
    """The price corrected on the vendor bill is applied to the whole receipt.

    It only happens when `product_cost_price_avco_sync` is installed, which is
    what replays the valuation chain, so the tests skip themselves when it is
    not there.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.partner = cls.env["res.partner"].create({"name": "Bill diff partner"})
        cls.categ = cls.env["product.category"].create(
            {
                "name": "Bill diff AVCO",
                "property_cost_method": "average",
                "property_valuation": "manual_periodic",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product billed at another price",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.categ.id,
                "standard_price": 0.0,
                "purchase_method": "receive",
            }
        )

    def setUp(self):
        super().setUp()
        if not hasattr(self.env["stock.valuation.layer"], "_cost_price_avco_sync"):
            raise unittest.SkipTest("product_cost_price_avco_sync is not installed")

    def _receive(self, quantity, price):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": quantity,
                            "price_unit": price,
                            "name": self.product.name,
                            "date_planned": fields.Datetime.now(),
                        }
                    )
                ],
            }
        )
        order.button_confirm()
        picking = order.picking_ids[:1]
        picking.move_line_ids[:1].quantity = quantity
        picking.move_line_ids.picked = True
        picking._action_done()
        return order, picking

    def _deliver(self, quantity):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "partner_id": self.partner.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": quantity,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids[:1].quantity = quantity
        picking.move_line_ids.picked = True
        picking._action_done()
        return picking

    def _bill(self, order, price_unit):
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "invoice_date": fields.Date.today(),
            }
        )
        bill.purchase_id = order
        bill._onchange_purchase_auto_complete()
        bill.invoice_line_ids.price_unit = price_unit
        bill.action_post()
        return bill

    def _layers(self):
        return self.env["stock.valuation.layer"].search(
            [("product_id", "=", self.product.id)], order="id"
        )

    def test_bill_price_difference_restates_the_receipt(self):
        order, picking = self._receive(10.0, 10.0)
        self._deliver(4.0)
        receipt_layer = picking.move_ids.stock_valuation_layer_ids
        out_layer = self._layers().filtered(lambda svl: svl.quantity < 0)
        self.assertAlmostEqual(out_layer.unit_cost, 10.0, 2)
        as_of = receipt_layer.create_date

        self._bill(order, 12.0)

        # The receipt itself, not only what is still on hand
        self.assertAlmostEqual(receipt_layer.unit_cost, 12.0, 2)
        self.assertAlmostEqual(receipt_layer.value, 120.0, 2)
        self.assertAlmostEqual(receipt_layer.remaining_value, 72.0, 2)
        # What already left follows, which is what the margin reads
        self.assertAlmostEqual(out_layer.unit_cost, 12.0, 2)
        self.assertAlmostEqual(out_layer.value, -48.0, 2)
        # And Odoo's own child layer is not added on top
        self.assertFalse(self._layers().filtered("stock_valuation_layer_id"))
        self.assertAlmostEqual(self.product.standard_price, 12.0, 2)
        # A valuation asked for a date before the bill comes out corrected:
        # 120 received minus the 48 delivered, instead of the 60 it showed
        # before the bill was posted
        self.assertAlmostEqual(
            self.product.with_context(to_date=as_of).value_svl, 72.0, 2
        )

    def test_bill_at_the_price_already_synced_changes_nothing(self):
        """Correcting the purchase order and then billing at that same price
        must not correct it twice."""
        order, _picking = self._receive(10.0, 10.0)
        self._deliver(4.0)
        order.order_line.price_unit = 12.0
        value_before = sum(self._layers().mapped("value"))

        self._bill(order, 12.0)

        self.assertFalse(self._layers().filtered("stock_valuation_layer_id"))
        self.assertAlmostEqual(sum(self._layers().mapped("value")), value_before, 2)
        self.assertAlmostEqual(self.product.standard_price, 12.0, 2)
