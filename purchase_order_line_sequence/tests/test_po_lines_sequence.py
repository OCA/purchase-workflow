# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 ForgeFlow, S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.exceptions import UserError
from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestPurchaseOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Useful models
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]
        cls.partner_id = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        product_uom_unit_round_1 = cls.env.ref("uom.product_uom_unit")
        cls.product_id_1 = cls.env["product.product"].create(
            {
                "name": "Large Desk",
                "standard_price": 1299.0,
                "list_price": 1799.0,
                "type": "consu",
                "weight": 9.54,
                "default_code": "E-COM09",
                "description_sale": "Minimalist wooden desk for executive use",
                "uom_id": product_uom_unit_round_1.id,
            }
        )

        cls.product_id_2 = cls.env["product.product"].create(
            {
                "name": "Conference Chair",
                "standard_price": 28.0,
                "list_price": 33.0,
                "type": "consu",
                "uom_id": product_uom_unit_round_1.id,
            }
        )

        cls.AccountInvoice = cls.env["account.move"]
        cls.AccountInvoiceLine = cls.env["account.move.line"]

        cls.category = cls.env["product.category"].create(
            {
                "name": "Test category",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
            }
        )

        cls.account_expense = cls.env["account.account"].create(
            {
                "name": "Expense",
                "code": "EXP00",
                "account_type": "liability_current",
                "reconcile": True,
            }
        )
        cls.account_payable = cls.env["account.account"].create(
            {
                "name": "Payable",
                "code": "PAY00",
                "account_type": "liability_payable",
                "reconcile": True,
            }
        )

        cls.category.property_account_expense_categ_id = cls.account_expense

        cls.category.property_stock_journal = cls.env["account.journal"].create(
            {"name": "Stock journal", "type": "sale", "code": "STK00"}
        )
        cls.product_id_1.categ_id = cls.category
        cls.product_id_2.categ_id = cls.category
        cls.partner_id.property_account_payable_id = cls.account_payable

    def _create_purchase_order(self):
        po_vals = {
            "partner_id": self.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id_1.name,
                        "product_id": self.product_id_1.id,
                        "product_qty": 5.0,
                        "product_uom_id": self.product_id_1.uom_id.id,
                        "price_unit": 500.0,
                        "date_planned": datetime.today(),
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": self.product_id_2.name,
                        "product_id": self.product_id_2.id,
                        "product_qty": 5.0,
                        "product_uom_id": self.product_id_2.uom_id.id,
                        "price_unit": 250.0,
                        "date_planned": datetime.today(),
                    },
                ),
            ],
        }

        return self.PurchaseOrder.create(po_vals)

    def test_purchase_order_line_sequence(self):
        self.po = self._create_purchase_order()

        po_form = Form(self.po)
        with po_form.order_line.new() as po_line_form:
            po_line_form.product_id = self.product_id_1
            self.assertEqual(po_line_form.sequence, self.po.max_line_sequence)

        self.po.button_confirm()

        move1 = self.env["stock.move"].search(
            [("purchase_line_id", "=", self.po.order_line[0].id)]
        )
        move2 = self.env["stock.move"].search(
            [("purchase_line_id", "=", self.po.order_line[1].id)]
        )

        self.assertEqual(
            self.po.order_line[0].visible_sequence,
            move1.sequence,
            "The Sequence of the Purchase Order Lines does not "
            "match to the Stock Moves",
        )
        self.assertEqual(
            self.po.order_line[1].visible_sequence,
            move2.sequence,
            "The Sequence of the Purchase Order Lines does not "
            "match to the Stock Moves",
        )

        self.po2 = self.po.copy()
        self.assertEqual(
            self.po.order_line[0].visible_sequence,
            self.po2.order_line[0].visible_sequence,
            "The Sequence is not copied properly",
        )
        self.assertEqual(
            self.po.order_line[1].visible_sequence,
            self.po2.order_line[1].visible_sequence,
            "The Sequence is not copied properly",
        )

    def test_purchase_order_line_sequence_with_section_note(self):
        """
        Verify that the sequence is correctly assigned to the move associated
        with the purchase order line it references.
        """
        po = self._create_purchase_order()
        self.PurchaseOrderLine.create(
            {
                "name": "Section 1",
                "display_type": "line_section",
                "order_id": po.id,
                "product_qty": 0,
            }
        )
        self.PurchaseOrderLine.create(
            {
                "name": self.product_id_1.name,
                "product_id": self.product_id_1.id,
                "product_qty": 15.0,
                "product_uom_id": self.product_id_1.uom_id.id,
                "price_unit": 150.0,
                "date_planned": datetime.today(),
                "order_id": po.id,
            }
        )
        self.PurchaseOrderLine.create(
            {
                "name": "Note 1",
                "display_type": "line_note",
                "order_id": po.id,
                "product_qty": 0,
            }
        )
        self.PurchaseOrderLine.create(
            {
                "name": self.product_id_2.name,
                "product_id": self.product_id_2.id,
                "product_qty": 1.0,
                "product_uom_id": self.product_id_2.uom_id.id,
                "price_unit": 50.0,
                "date_planned": datetime.today(),
                "order_id": po.id,
            }
        )
        po.button_confirm()

        moves = po.picking_ids[0].move_ids
        self.assertNotEqual(len(po.order_line), len(moves))

        for move in moves:
            self.assertEqual(move.sequence, move.purchase_line_id.visible_sequence)

    def test_write_purchase_order_line(self):
        """
        Verify that the sequence is correctly assigned to the move associated
        with the purchase order line it references when you modify it.
        """
        po = self._create_purchase_order()
        po.button_confirm()

        po.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_id_2.name,
                            "product_id": self.product_id_2.id,
                            "product_qty": 2,
                            "product_uom_id": self.product_id_2.uom_id.id,
                            "price_unit": 30,
                            "date_planned": datetime.today(),
                        },
                    )
                ]
            }
        )

        moves = po.picking_ids[0].move_ids
        for move in moves:
            self.assertEqual(move.sequence, move.purchase_line_id.visible_sequence)

    def test_invoice_sequence(self):
        """
        Verify that the sequence is correctly assigned to the account move associated
        with the purchase order line it references.
        """
        po = self._create_purchase_order()
        po.button_confirm()
        po.order_line.qty_received = 5
        result = po.action_create_invoice()
        self.invoice = self.AccountInvoice.browse(result["res_id"])
        self.assertEqual(
            str(po.order_line[0].visible_sequence),
            self.invoice.line_ids[0].related_po_sequence,
        )
        self.assertEqual(
            str(po.order_line[1].visible_sequence),
            self.invoice.line_ids[1].related_po_sequence,
        )


def test_invoice_multiple_orders_sequence(self):
    """
    Verify that the sequence is correctly assigned to the account move associated
    with the purchase order line it references,
    when adding different POs to the same invoice.
    Format expected:
    - PO12345/1  -  PO Name + "/" + Sequence
    """

    po1 = self._create_purchase_order()
    po2 = self._create_purchase_order()

    po1.button_confirm()
    po2.button_confirm()

    po1.order_line.qty_received = 5
    po2.order_line.qty_received = 5

    # Create first invoice
    res1 = po1.action_create_invoice()
    invoice = self.AccountInvoice.browse(res1["res_id"])

    # Add second PO lines into SAME invoice
    res2 = po2.action_create_invoice()
    invoice2 = self.AccountInvoice.browse(res2["res_id"])

    # Merge invoices (this is the critical step)
    invoice.write(
        {
            "invoice_line_ids": [
                (4, line.id) for line in invoice2.line_ids if not line.display_type
            ]
        }
    )

    # Ensure recompute
    invoice._compute_related_po_sequence()

    lines = invoice.line_ids.filtered(lambda line: not line.display_type)

    # Expected formatted values
    expected_po1 = f"{po1.name}/{po1.order_line[0].visible_sequence}"
    expected_po2 = f"{po2.name}/{po2.order_line[0].visible_sequence}"

    sequences = lines.mapped("related_po_sequence")

    self.assertIn(expected_po1, sequences)
    self.assertIn(expected_po2, sequences)

    # Optional strict check: ALL lines must be prefixed now
    for seq in sequences:
        self.assertIn(
            "/", seq, "Sequence should include PO name when multiple POs exist"
        )


def test_onchange_sequence_forbidden_on_purchase_move(self):
    """
    Ensure that changing the sequence on a stock move linked to a purchase line
    raises a UserError via the onchange.
    """
    po = self._create_purchase_order()
    po.button_confirm()

    move = self.env["stock.move"].search(
        [("purchase_line_id", "=", po.order_line[0].id)],
        limit=1,
    )
    self.assertTrue(move, "Stock move should exist")

    # Simulate UI form to trigger onchange
    with self.assertRaises(UserError):
        with Form(move) as move_form:
            move_form.sequence = move.sequence + 10
