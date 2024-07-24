from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestPurchaseReceiptThreshold(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Partner = cls.env["res.partner"]
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.ResConfigSettings = cls.env["res.config.settings"]
        cls.Product = cls.env["product.product"]
        cls.Journal = cls.env["account.journal"]

        # Set up company with receipt_threshold
        cls.company = cls.env.ref("base.main_company")
        cls.company.write({"receipt_threshold": 0.1})
        # Set up a purchase journal for the company
        cls.journal = cls.Journal.create(
            {
                "name": "Purchase Journal",
                "type": "purchase",
                "code": "PURCHASE",
                "company_id": cls.company.id,
            }
        )

        # Set up partner with use_threshold
        cls.partner = cls.Partner.create(
            {
                "name": "Test Partner",
                "use_threshold": True,
            }
        )

        # Set up partner without use_threshold
        cls.partner_no_threshold = cls.Partner.create(
            {
                "name": "Test Partner No Threshold",
                "use_threshold": False,
            }
        )

        # Set up product with purchase_method
        cls.product = cls.Product.create(
            {
                "name": "Test Product",
                "type": "product",
                "purchase_method": "receive",
            }
        )

    def test_01_field_visibility_accessibility(self):
        """Test field visibility and accessibility based on user groups."""
        # Test with a user that belongs to the groups:
        # Administration / Settings (base.group_system)
        # Purchase / Administrator (purchase.group_purchase_manager)
        purchase_admin = self.env["res.users"].create(
            {
                "name": "Purchase Manager",
                "login": "purchase_manager",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_system").id,
                            self.env.ref("purchase.group_purchase_manager").id,
                        ],
                    )
                ],
            }
        )

        config = self.ResConfigSettings.with_user(purchase_admin).create(
            {"receipt_threshold": 0.2}
        )
        self.assertEqual(config.receipt_threshold, 0.2)

        partner = self.Partner.create({"name": "Test Partner"})
        partner.with_user(purchase_admin).write({"use_threshold": True})
        self.assertTrue(partner.use_threshold)

        # Test with a user that belongs to the groups:
        # Purchase / User (purchase.group_purchase_user)
        # Extra Rights / Contact Creation (base.group_partner_manager)
        purchase_user = self.env["res.users"].create(
            {
                "name": "Purchase User",
                "login": "purchase_user",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("purchase.group_purchase_user").id,
                            self.env.ref("base.group_partner_manager").id,
                        ],
                    )
                ],
            }
        )

        with self.assertRaises(AccessError) as ctx:
            config.with_user(purchase_user).receipt_threshold = 0.1

        self.assertIn("Administration/Settings", str(ctx.exception))
        with self.assertRaises(AccessError) as ctx:
            partner.with_user(purchase_user).use_threshold = False

        self.assertIn(
            "use_threshold (allowed for groups 'Purchase / Administrator')",
            str(ctx.exception),
        )

    def test_02_field_population(self):
        """Test that fields in purchase.order.line are populated correctly."""
        po = self.PurchaseOrder.create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_qty": 10,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )

        po_line = po.order_line[0]
        self.assertEqual(po_line.receipt_threshold, self.company.receipt_threshold)
        self.assertEqual(po_line.use_threshold, self.partner.use_threshold)

    def test_03_purchase_order_within_threshold(self):
        """Test behavior for a purchase order with use_threshold = True."""
        po = self.PurchaseOrder.create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_qty": 10,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        po_line = po.order_line[0]
        po.button_confirm()
        self.assertEqual(po.state, "purchase")

        picking = po.picking_ids[0]
        picking.picking_type_id.write({"create_backorder": "always"})
        picking.move_ids.write({"quantity": 9})
        picking.button_validate()

        self.assertEqual(picking.state, "done")
        self.assertEqual(po_line.qty_received, 9)
        self.assertTrue(po_line._check_threshold(po_line.qty_received))
        self.assertEqual(po.receipt_status, "full")
        self.assertEqual(po.invoice_status, "to invoice")

        # Create the invoice
        po.action_create_invoice()
        invoice = po.invoice_ids
        self.assertEqual(invoice.invoice_line_ids.quantity, 9)
        self.assertEqual(po.invoice_status, "invoiced")

        # Verify backorder creation
        backorders = self.StockPicking.search([("backorder_id", "=", picking.id)])
        self.assertFalse(backorders)
        self.assertFalse(picking.backorder_ids)
        self.assertEqual(len(po.picking_ids), 1)

    def test_04_purchase_order_outside_threshold(self):
        """Test behavior for a purchase order with use_threshold = True."""
        po = self.PurchaseOrder.create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_qty": 10,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        po_line = po.order_line[0]
        po.button_confirm()
        self.assertEqual(po.state, "purchase")

        picking = po.picking_ids[0]
        picking.picking_type_id.write({"create_backorder": "always"})
        picking.move_ids.write({"quantity": 7})
        picking.button_validate()

        self.assertEqual(picking.state, "done")
        self.assertEqual(po_line.qty_received, 7)
        self.assertFalse(po_line._check_threshold(po_line.qty_received))
        self.assertEqual(po.receipt_status, "partial")
        self.assertEqual(po.invoice_status, "to invoice")

        # Create the invoice
        po.action_create_invoice()
        invoice = po.invoice_ids
        self.assertEqual(invoice.invoice_line_ids.quantity, 7)
        self.assertEqual(po.invoice_status, "invoiced")

        # Verify backorder creation
        backorders = self.StockPicking.search([("backorder_id", "=", picking.id)])
        self.assertTrue(backorders)
        self.assertTrue(picking.backorder_ids)
        self.assertEqual(len(backorders), 1)
        self.assertEqual(len(po.picking_ids), 2)
        self.assertEqual(backorders.move_ids.quantity, 3)

    def test_05_purchase_order_without_threshold(self):
        """Test behavior for a purchase order with use_threshold = False."""
        po = self.PurchaseOrder.create(
            {
                "partner_id": self.partner_no_threshold.id,
                "company_id": self.company.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_qty": 10,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        po_line = po.order_line[0]
        po.button_confirm()
        self.assertEqual(po.state, "purchase")

        picking = po.picking_ids[0]
        picking.picking_type_id.write({"create_backorder": "always"})
        picking.move_ids.write({"quantity": 9})
        picking.button_validate()

        self.assertEqual(picking.state, "done")
        self.assertEqual(po_line.qty_received, 9)
        self.assertFalse(po_line._check_threshold(po_line.qty_received))
        self.assertEqual(po.receipt_status, "partial")
        self.assertEqual(po.invoice_status, "to invoice")

        # Create the invoice
        po.action_create_invoice()
        invoice = po.invoice_ids
        self.assertEqual(invoice.invoice_line_ids.quantity, 9)
        self.assertEqual(po.invoice_status, "invoiced")

        # Verify backorder creation
        backorders = self.StockPicking.search([("backorder_id", "=", picking.id)])
        self.assertTrue(backorders)
        self.assertTrue(picking.backorder_ids)
        self.assertEqual(len(backorders), 1)
        self.assertEqual(len(po.picking_ids), 2)
        self.assertEqual(backorders.move_ids.quantity, 1)
