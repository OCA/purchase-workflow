# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


from unittest.mock import patch

from odoo import Command, fields
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestAutoBillOnReceipt(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.picking_type_in = cls.warehouse.in_type_id
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.vendor_auto = cls.env["res.partner"].create(
            {"name": "Auto Vendor", "auto_bill_on_receipt": "auto"}
        )
        cls.vendor_no_auto = cls.env["res.partner"].create(
            {"name": "No-Auto Vendor", "auto_bill_on_receipt": "no_auto"}
        )

        cls.product = cls._create_product("Storable Product")
        cls.product_billed_on_order = cls._create_product(
            "Billed On Order Product", purchase_method="purchase"
        )

    @classmethod
    def _create_product(cls, name, **vals):
        return cls.env["product.product"].create(
            {
                "name": name,
                "is_storable": True,
                "standard_price": 10.0,
                "list_price": 20.0,
                "uom_id": cls.uom_unit.id,
                **vals,
            }
        )

    def _line(self, product, qty=1.0, price=10.0):
        return Command.create(
            {
                "product_id": product.id,
                "product_qty": qty,
                "product_uom_id": product.uom_id.id,
                "price_unit": price,
                "tax_ids": [Command.clear()],
            }
        )

    def _section(self, name):
        return Command.create(
            {"display_type": "line_section", "name": name, "product_qty": 0.0}
        )

    def _create_po(self, lines, partner=None, confirm=True):
        po = self.env["purchase.order"].create(
            {"partner_id": (partner or self.vendor).id, "order_line": lines}
        )
        if confirm:
            po.button_confirm()
        return po

    def _run_auto_bill_cron(self):
        # button_validate only triggers the cron; run it explicitly so the
        # bills are created within the test transaction.
        self.env["stock.picking"]._cron_auto_bill()

    def _receive(self, po, quantity=None, run_cron=True):
        pickings = po.picking_ids.filtered(lambda p: p.state != "done")
        if quantity is not None:
            pickings.move_ids.quantity = quantity
        pickings.with_context(skip_backorder=True).button_validate()
        if run_cron:
            self._run_auto_bill_cron()
        return pickings

    def _validate(self, picking, quantity):
        picking.move_ids.quantity = quantity
        picking.with_context(skip_backorder=True).button_validate()
        self._run_auto_bill_cron()

    def _return(self, picking, quantity=None, to_refund=True, run_cron=True):
        """Create and validate a return for the given picking."""
        return_wizard = (
            self.env["stock.return.picking"]
            .with_context(active_id=picking.id, active_model="stock.picking")
            .create({})
        )
        for move_line in return_wizard.product_return_moves:
            move_line.to_refund = to_refund
            if quantity is not None:
                move_line.quantity = quantity
        action = return_wizard.action_create_returns()
        return_picking = self.env["stock.picking"].browse(action["res_id"])
        if quantity is not None:
            return_picking.move_ids.quantity = quantity
        return_picking.with_context(skip_backorder=True).button_validate()
        if run_cron:
            self._run_auto_bill_cron()
        return return_picking

    def _bills_of(self, po):
        return po.invoice_ids.sorted("id")

    def test_company_default_creates_bill(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po([self._line(self.product, 5.0)])
        picking = self._receive(po)
        bills = self._bills_of(po)
        self.assertEqual(len(bills), 1)
        self.assertEqual(bills.state, "posted")
        self.assertEqual(bills.invoice_line_ids.quantity, 5.0)
        self.assertEqual(bills.invoice_origin, po.name)
        self.assertEqual(bills.invoice_date, picking.date_done.date())

    def test_company_default_off_no_bill(self):
        self.company.auto_bill_on_receipt = False
        po = self._create_po([self._line(self.product, 5.0)])
        self._receive(po)
        self.assertFalse(self._bills_of(po))

    def test_vendor_override_auto_with_company_off(self):
        self.company.auto_bill_on_receipt = False
        po = self._create_po([self._line(self.product, 3.0)], partner=self.vendor_auto)
        self._receive(po)
        bills = self._bills_of(po)
        self.assertEqual(len(bills), 1)
        self.assertEqual(bills.state, "posted")

    def test_vendor_override_no_auto_with_company_on(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po(
            [self._line(self.product, 2.0)], partner=self.vendor_no_auto
        )
        self._receive(po)
        self.assertFalse(self._bills_of(po))

    def test_block_auto_bill_on_po(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po([self._line(self.product, 4.0)])
        po.block_auto_bill = True
        self._receive(po)
        self.assertFalse(self._bills_of(po))

    def test_billed_on_ordered_qty_not_auto_billed(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po(
            [
                self._line(self.product, 2.0),
                self._line(self.product_billed_on_order, 3.0, price=20.0),
            ]
        )
        self._receive(po)
        bills = self._bills_of(po)
        self.assertEqual(len(bills), 1)
        self.assertEqual(bills.state, "posted")
        # Only the line billed on received quantities is invoiced.
        self.assertEqual(bills.invoice_line_ids.product_id, self.product)
        self.assertEqual(bills.invoice_line_ids.quantity, 2.0)

    def test_partial_receipt_creates_one_bill_per_receipt(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po([self._line(self.product, 10.0)])
        first_picking = po.picking_ids
        self._validate(first_picking, 4.0)
        bills = self._bills_of(po)
        self.assertEqual(len(bills), 1)
        self.assertEqual(bills.invoice_line_ids.quantity, 4.0)
        self.assertEqual(bills.state, "posted")

        backorder = po.picking_ids - first_picking
        self.assertEqual(len(backorder), 1)
        self._validate(backorder, 6.0)
        bills = self._bills_of(po)
        self.assertEqual(len(bills), 2)
        second_bill = bills - bills[0]
        self.assertEqual(second_bill.invoice_line_ids.quantity, 6.0)
        self.assertEqual(second_bill.state, "posted")

    def test_receipt_without_po_does_nothing(self):
        self.company.auto_bill_on_receipt = True
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.move_ids.quantity = 1.0
        picking.move_ids.picked = True
        picking.button_validate()
        self.assertFalse(
            self.env["account.move"].search(
                [
                    ("move_type", "=", "in_invoice"),
                    ("invoice_origin", "like", picking.name),
                ]
            )
        )

    def test_idempotent_on_second_call(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po([self._line(self.product, 5.0)])
        self._receive(po)
        self.assertEqual(len(self._bills_of(po)), 1)
        po.picking_ids._auto_create_vendor_bill()
        self.assertEqual(len(self._bills_of(po)), 1)

    def test_sections_carried_over_only_when_needed(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po(
            [
                self._section("Billed Section"),
                self._line(self.product, 2.0),
                self._section("Skipped Section"),
                self._line(self.product_billed_on_order, 3.0, price=20.0),
            ]
        )
        self._receive(po)
        bills = self._bills_of(po)
        self.assertEqual(len(bills), 1)

        sections = bills.invoice_line_ids.filtered(
            lambda line: line.display_type == "line_section"
        )
        # Only the section preceding an eligible line is carried over.
        self.assertEqual(sections.name, "Billed Section")

        product_lines = bills.invoice_line_ids.filtered(
            lambda line: line.display_type == "product"
        )
        self.assertEqual(product_lines.product_id, self.product)
        # Section header keeps its place above its product line.
        self.assertLess(sections.sequence, product_lines.sequence)

    def test_commercial_partner_setting_applies_to_contact(self):
        # A PO placed on a child contact uses the vendor company's policy.
        self.company.auto_bill_on_receipt = False
        vendor = self.env["res.partner"].create(
            {"name": "Vendor Co", "is_company": True, "auto_bill_on_receipt": "auto"}
        )
        contact = self.env["res.partner"].create(
            {"name": "Vendor Contact", "parent_id": vendor.id}
        )
        po = self._create_po([self._line(self.product, 3.0)], partner=contact)
        self._receive(po)
        bills = self._bills_of(po)
        self.assertEqual(len(bills), 1)
        self.assertEqual(bills.state, "posted")

    def test_does_not_over_bill_when_partially_invoiced(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po([self._line(self.product, 10.0)])
        # Validate the full receipt but hold the cron so we can inject a
        # manual bill before the auto-bill runs.
        self._receive(po, run_cron=False)
        # Manually bill 4 of the 10 received units.
        po.action_create_invoice()
        manual_bill = po.invoice_ids
        manual_bill.invoice_line_ids.quantity = 4.0
        manual_bill.invoice_date = fields.Date.today()
        manual_bill.action_post()
        self.assertEqual(po.order_line.qty_to_invoice, 6.0)
        # Now let the auto-bill cron run: it must bill only the remaining 6.
        self._run_auto_bill_cron()
        auto_bill = po.invoice_ids - manual_bill
        self.assertEqual(len(auto_bill), 1)
        self.assertEqual(auto_bill.invoice_line_ids.quantity, 6.0)
        # The line is fully invoiced, not over-invoiced.
        self.assertEqual(po.order_line.qty_invoiced, 10.0)

    @mute_logger(
        "odoo.addons.purchase_auto_bill_on_receipt.models.purchase_order",
        "odoo.addons.purchase_auto_bill_on_receipt.models.stock_picking",
    )
    def test_creation_failure_logs_to_chatter(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po([self._line(self.product, 5.0)])
        self._receive(po, run_cron=False)
        with patch.object(
            type(po),
            "_auto_bill_create",
            side_effect=Exception("test creation error"),
        ):
            self._run_auto_bill_cron()
        self.assertFalse(self._bills_of(po))
        self.assertIn("Auto bill creation failed", po.message_ids[0].body)
        activity = po.activity_ids.filtered(
            lambda a: a.activity_type_id == self.env.ref("mail.mail_activity_data_todo")
        )
        self.assertTrue(activity)

    @mute_logger(
        "odoo.addons.purchase_auto_bill_on_receipt.models.purchase_order",
        "odoo.addons.purchase_auto_bill_on_receipt.models.stock_picking",
    )
    def test_posting_failure_logs_to_chatter(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po([self._line(self.product, 5.0)])
        self._receive(po, run_cron=False)
        with patch.object(
            type(self.env["account.move"]),
            "action_post",
            side_effect=Exception("test posting error"),
        ):
            self._run_auto_bill_cron()
        bills = self._bills_of(po)
        self.assertEqual(len(bills), 1)
        self.assertEqual(bills.state, "draft")
        self.assertIn("Auto bill posting failed", po.message_ids[0].body)
        activity = po.activity_ids.filtered(
            lambda a: a.activity_type_id == self.env.ref("mail.mail_activity_data_todo")
        )
        self.assertTrue(activity)

    # ── Return / Credit Note tests ──

    def test_return_with_to_refund_creates_credit_note(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po([self._line(self.product, 5.0)])
        picking = self._receive(po)
        self.assertEqual(len(self._bills_of(po)), 1)
        # Return 2 units with to_refund=True
        self._return(picking, quantity=2.0, to_refund=True)
        invoices = self._bills_of(po)
        self.assertEqual(len(invoices), 2)
        credit_note = invoices.filtered(lambda m: m.move_type == "in_refund")
        self.assertEqual(len(credit_note), 1)
        self.assertEqual(credit_note.state, "posted")
        self.assertEqual(credit_note.invoice_line_ids.quantity, 2.0)

    def test_return_without_to_refund_no_credit_note(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po([self._line(self.product, 5.0)])
        picking = self._receive(po)
        self._return(picking, quantity=2.0, to_refund=False)
        invoices = self._bills_of(po)
        # Only the original bill, no credit note.
        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices.move_type, "in_invoice")

    def test_return_auto_bill_disabled_no_credit_note(self):
        self.company.auto_bill_on_receipt = False
        po = self._create_po(
            [self._line(self.product, 5.0)], partner=self.vendor_no_auto
        )
        picking = self._receive(po)
        self._return(picking, quantity=2.0, to_refund=True)
        self.assertFalse(po.invoice_ids.filtered(lambda m: m.move_type == "in_refund"))

    @mute_logger(
        "odoo.addons.purchase_auto_bill_on_receipt.models.purchase_order",
        "odoo.addons.purchase_auto_bill_on_receipt.models.stock_picking",
    )
    def test_return_creation_failure_logs_to_chatter(self):
        self.company.auto_bill_on_receipt = True
        po = self._create_po([self._line(self.product, 5.0)])
        picking = self._receive(po)
        self._return(picking, quantity=2.0, run_cron=False)
        with patch.object(
            type(po),
            "_auto_bill_create",
            side_effect=Exception("test refund creation error"),
        ):
            self._run_auto_bill_cron()
        self.assertFalse(po.invoice_ids.filtered(lambda m: m.move_type == "in_refund"))
        self.assertIn("Auto credit note creation failed", po.message_ids[0].body)
