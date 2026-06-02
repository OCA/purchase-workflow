# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from freezegun import freeze_time

from odoo import Command

from .common import PurchaseStockDateDoneRevaluationCommon


class TestPurchaseStockDateDoneRevaluation(PurchaseStockDateDoneRevaluationCommon):
    @freeze_time("2026-03-15")
    def test_revaluation_on_date_done_change_pre_bill(self):
        _, receipt, move = self._receive_po()
        # Back-date to DATE_1 (rate 1.0): 1000 EUR -> 1000 company.
        receipt.date_done = datetime(2026, 3, 1, 8, 0, 0)
        self.assertEqual(move.date, datetime(2026, 3, 1, 8, 0, 0))
        self.assertAlmostEqual(move.value, 1000.0, places=2)
        # Move to DATE_2 (rate 2.0): 1000 EUR -> 500 company.
        receipt.date_done = datetime(2026, 3, 10, 8, 0, 0)
        self.assertAlmostEqual(move.value, 500.0, places=2)

    @freeze_time("2026-03-15")
    def test_bill_governs_and_skip_if_billed(self):
        po, receipt, move = self._receive_po()
        receipt.date_done = datetime(2026, 3, 1, 8, 0, 0)
        self.assertAlmostEqual(move.value, 1000.0, places=2)

        # Post a vendor bill dated DATE_1 (rate 1.0) -> bill value 1000.
        po.action_create_invoice()
        bill = po.invoice_ids
        bill.invoice_date = "2026-03-01"
        bill.action_post()
        self.assertTrue(move._is_purchase_billed())
        self.assertAlmostEqual(move.value, 1000.0, places=2)

        # Once billed, changing the effective date must NOT revalue: the bill
        # governs the value. Our hook skips.
        receipt.date_done = datetime(2026, 3, 10, 8, 0, 0)
        self.assertEqual(move.date, datetime(2026, 3, 10, 8, 0, 0))
        self.assertAlmostEqual(
            move.value, 1000.0, places=2, msg="Billed move must not revalue from date"
        )

    @freeze_time("2026-03-15")
    def test_non_purchase_move_not_revalued(self):
        # An incoming move without a purchase line is not a candidate; its value
        # stays driven by standard price, untouched by date edits.
        self.product.standard_price = 7.0
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.company.id)], limit=1
        )
        picking_type = warehouse.in_type_id
        dest = picking_type.default_location_dest_id or warehouse.lot_stock_id
        receipt = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": dest.id,
                "partner_id": self.partner.id,
                "picking_type_id": picking_type.id,
                "move_ids": [
                    Command.create(
                        {
                            "location_id": self.supplier_location.id,
                            "location_dest_id": dest.id,
                            "product_id": self.product.id,
                            "product_uom_qty": 5.0,
                        }
                    )
                ],
            }
        )
        receipt.action_confirm()
        receipt.move_ids.quantity = 5.0
        receipt.move_ids.picked = True
        receipt.button_validate()
        move = receipt.move_ids
        self.assertFalse(move._is_date_done_revaluation_candidate())
        value_before = move.value
        receipt.date_done = datetime(2026, 3, 1, 8, 0, 0)
        self.assertEqual(move.value, value_before)
