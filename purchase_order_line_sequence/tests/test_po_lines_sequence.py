# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tests import common, tagged
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


@tagged("post_install", "-at_install")
class TestPurchaseOrder(common.TransactionCase):
    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        # Useful models
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseOrderLine = self.env["purchase.order.line"]
        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.product_id_2 = self.env.ref("product.product_product_11")

        self.AccountInvoice = self.env["account.move"]
        self.AccountInvoiceLine = self.env["account.move.line"]

        self.category = self.env.ref("product.product_category_1").copy(
            {
                "name": "Test category",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
            }
        )

        self.account_expense = self.env["account.account"].create(
            {
                "name": "Expense",
                "code": "EXP00",
                "account_type": "liability_current",
                "reconcile": True,
            }
        )
        self.account_payable = self.env["account.account"].create(
            {
                "name": "Payable",
                "code": "PAY00",
                "account_type": "liability_payable",
                "reconcile": True,
            }
        )

        self.category.property_account_expense_categ_id = self.account_expense

        self.category.property_stock_journal = self.env["account.journal"].create(
            {"name": "Stock journal", "type": "sale", "code": "STK00"}
        )
        self.product_id_1.categ_id = self.category
        self.product_id_2.categ_id = self.category
        self.partner_id.property_account_payable_id = self.account_payable

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
                        "product_uom": self.product_id_1.uom_po_id.id,
                        "price_unit": 500.0,
                        "date_planned": datetime.today().strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT
                        ),
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": self.product_id_2.name,
                        "product_id": self.product_id_2.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_2.uom_po_id.id,
                        "price_unit": 250.0,
                        "date_planned": datetime.today().strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT
                        ),
                    },
                ),
            ],
        }

        return self.PurchaseOrder.create(po_vals)

    def test_purchase_order_line_sequence(self):

        self.po = self._create_purchase_order()
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
                "product_uom": self.product_id_1.uom_po_id.id,
                "price_unit": 150.0,
                "date_planned": datetime.today().strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT
                ),
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
                "product_uom": self.product_id_2.uom_po_id.id,
                "price_unit": 50.0,
                "date_planned": datetime.today().strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT
                ),
                "order_id": po.id,
            }
        )
        po.button_confirm()

        moves = po.picking_ids[0].move_ids_without_package
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
                            "product_uom": self.product_id_2.uom_id.id,
                            "price_unit": 30,
                            "date_planned": datetime.today().strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT
                            ),
                        },
                    )
                ]
            }
        )

        moves = po.picking_ids[0].move_ids_without_package
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
        po = self._create_purchase_order()
        po.button_confirm()
        po.order_line.qty_received = 5
        po2 = self._create_purchase_order()
        po2.button_confirm()
        po2.order_line.qty_received = 2

        orders = self.PurchaseOrder.search([("id", "in", [po.id, po2.id])])
        result = orders.action_create_invoice()
        invoice = self.AccountInvoice.search([("id", "=", result["res_id"])], limit=1)

        self.assertTrue(invoice)
        self.assertTrue(len(invoice.invoice_origin.split(",")), 2)

        self.assertEqual(
            invoice.invoice_line_ids[0].related_po_sequence,
            "{}/{}".format(po2.name, po2.order_line[0].visible_sequence),
        )
        self.assertEqual(
            invoice.invoice_line_ids[3].related_po_sequence,
            "{}/{}".format(po.name, po.order_line[1].visible_sequence),
        )
