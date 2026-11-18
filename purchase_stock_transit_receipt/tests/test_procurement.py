# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta
from unittest.mock import patch

from odoo import Command, fields

from .common import TransitReceiptCommon


class TestProcurement(TransitReceiptCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        mto_route = cls.env.ref("stock.route_warehouse0_mto")
        mto_route.active = True
        cls.product.write(
            {
                "route_ids": [
                    Command.set(
                        [
                            mto_route.id,
                            cls.env.ref("purchase_stock.route_warehouse0_buy").id,
                        ]
                    )
                ],
                "seller_ids": [
                    Command.create({"partner_id": cls.supplier.id, "price": 10.0})
                ],
            }
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

    def _procure(self):
        ProcurementGroup = self.env["procurement.group"]
        group = ProcurementGroup.create({"name": "Sale"})
        ProcurementGroup.run(
            [
                ProcurementGroup.Procurement(
                    self.product,
                    5.0,
                    self.product.uom_id,
                    self.customer_location,
                    group.name,
                    group.name,
                    self.warehouse.company_id,
                    {
                        "warehouse_id": self.warehouse,
                        "group_id": group,
                        "date_deadline": fields.Datetime.now() + timedelta(days=10),
                    },
                )
            ]
        )
        return self.env["stock.picking"].search([("group_id", "=", group.id)])

    def _purchase(self):
        return self.env["purchase.order"].search(
            [("partner_id", "=", self.supplier.id)]
        )

    def _require_transit_receipt(self):
        return patch.object(
            type(self.env["purchase.order"]),
            "_requires_transit_receipt",
            lambda order: order.partner_id == self.supplier,
        )

    def test_transit_purchase(self):
        with self._require_transit_receipt():
            delivery = self._procure()
        purchase = self._purchase()
        self.assertEqual(purchase.picking_type_id, self.warehouse.transit_in_type_id)
        purchase.button_confirm()
        transit_receipt = purchase.picking_ids
        self.assertFalse(transit_receipt.move_ids.move_dest_ids)
        self._validate(transit_receipt)
        physical_receipt = self._next_picking(transit_receipt)
        self.assertEqual(physical_receipt.state, "assigned")
        self.assertEqual(physical_receipt.move_ids.move_dest_ids, delivery.move_ids)
        self.assertEqual(delivery.state, "waiting")
        self.assertEqual(purchase.order_line.qty_received, 0)
        self._validate(physical_receipt)
        self.assertEqual(purchase.order_line.qty_received, 5)
        self.assertEqual(delivery.state, "assigned")

    def test_merge_into_draft_transit_purchase(self):
        incoterm = self.env["account.incoterms"].create(
            {"name": "Transit", "code": "TT1", "transit_receipt": True}
        )
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "picking_type_id": self.warehouse.in_type_id.id,
                "user_id": False,
            }
        )
        purchase.incoterm_id = incoterm
        self.assertEqual(purchase.picking_type_id, self.warehouse.transit_in_type_id)
        self._procure()
        self.assertEqual(self._purchase(), purchase)
        self.assertEqual(purchase.order_line.product_qty, 5)

    def test_partial_transit_receipt(self):
        with self._require_transit_receipt():
            delivery = self._procure()
        purchase = self._purchase()
        purchase.button_confirm()
        transit_receipt = purchase.picking_ids
        self._validate(transit_receipt, quantity=2)
        backorder = transit_receipt.backorder_ids
        self._validate(backorder)
        physical_receipts = self._next_picking(transit_receipt | backorder)
        self.assertEqual(sum(physical_receipts.move_ids.mapped("product_uom_qty")), 5)
        self.assertEqual(physical_receipts.move_ids.move_dest_ids, delivery.move_ids)
        self._validate(physical_receipts)
        self.assertEqual(purchase.order_line.qty_received, 5)
        self.assertEqual(delivery.state, "assigned")
        self.assertEqual(delivery.move_ids.quantity, 5)

    def test_purchase_without_transit(self):
        delivery = self._procure()
        purchase = self._purchase()
        self.assertEqual(purchase.picking_type_id, self.warehouse.in_type_id)
        purchase.button_confirm()
        receipt = purchase.picking_ids
        self.assertEqual(receipt.move_ids.move_dest_ids, delivery.move_ids)
        self.assertFalse(purchase.order_line.move_dest_ids)
        self._validate(receipt)
        self.assertEqual(purchase.order_line.qty_received, 5)
        self.assertEqual(delivery.state, "assigned")

    def _confirmed_transit_purchase(self):
        with self._require_transit_receipt():
            delivery = self._procure()
        purchase = self._purchase()
        purchase.button_confirm()
        return purchase, delivery

    def test_cancel_transit_receipt(self):
        purchase, delivery = self._confirmed_transit_purchase()
        purchase.picking_ids.action_cancel()
        self.assertEqual(delivery.move_ids.procure_method, "make_to_stock")
        self.assertEqual(delivery.state, "confirmed")

    def test_cancel_transit_receipt_backorder(self):
        purchase, delivery = self._confirmed_transit_purchase()
        transit_receipt = purchase.picking_ids
        self._validate(transit_receipt, quantity=2)
        transit_receipt.backorder_ids.action_cancel()
        self.assertEqual(delivery.move_ids.procure_method, "make_to_order")
        self.assertEqual(delivery.state, "waiting")

    def test_delay_alert_from_transit_receipt(self):
        purchase, delivery = self._confirmed_transit_purchase()
        late_date = delivery.move_ids.date + timedelta(days=5)
        purchase.picking_ids.move_ids.date = late_date
        self.assertEqual(delivery.move_ids.delay_alert_date, late_date)

    def test_date_deadline_propagated_until_transit_receipt(self):
        purchase, delivery = self._confirmed_transit_purchase()
        transit_move = purchase.picking_ids.move_ids
        delivery_deadline = delivery.move_ids.date_deadline
        new_date = transit_move.date_deadline + timedelta(days=3)
        purchase.order_line.date_planned = new_date
        self.assertEqual(transit_move.date_deadline, new_date)
        self.assertEqual(
            delivery.move_ids.date_deadline, delivery_deadline + timedelta(days=3)
        )
        self._validate(purchase.picking_ids)
        delivery_deadline = delivery.move_ids.date_deadline
        purchase.order_line.date_planned = new_date + timedelta(days=3)
        self.assertEqual(delivery.move_ids.date_deadline, delivery_deadline)

    def test_increased_quantity_keeps_delivery_demand(self):
        purchase, delivery = self._confirmed_transit_purchase()
        purchase.order_line.product_qty = 7
        transit_receipt = purchase.picking_ids
        self.assertEqual(transit_receipt.move_ids.product_uom_qty, 7)
        self._validate(transit_receipt)
        physical_receipt = self._next_picking(transit_receipt)
        self.assertEqual(physical_receipt.move_ids.move_dest_ids, delivery.move_ids)
        self._validate(physical_receipt)
        self.assertEqual(purchase.order_line.qty_received, 7)
        self.assertEqual(delivery.move_ids.product_uom_qty, 5)
        self.assertEqual(delivery.move_ids.quantity, 5)
