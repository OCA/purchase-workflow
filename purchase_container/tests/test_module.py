from datetime import date, timedelta

from odoo import Command, fields
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseContainerBase(BaseCommon):
    """Base test class with common setup for purchase container tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Supplier"})
        # Handle base_unit_count: website_sale adds NOT NULL constraint but may not be
        # loaded in test registry. Set DB default to handle schema mismatch.
        if "base_unit_count" not in cls.env["product.template"]._fields:
            cls.env.cr.execute(
                """
                ALTER TABLE product_template
                ALTER COLUMN base_unit_count SET DEFAULT 0;
                ALTER TABLE product_product
                ALTER COLUMN base_unit_count SET DEFAULT 0;
                """
            )
        product_vals = {"name": "Test Product"}
        if "base_unit_count" in cls.env["product.template"]._fields:
            product_vals["base_unit_count"] = 1
        product_tmpl = cls.env["product.template"].create(product_vals)
        cls.product = product_tmpl.product_variant_id
        cls.cont_a = cls.env["purchase.container"].create({"code": "AA"})
        cls.cont_b = cls.env["purchase.container"].create({"code": "BB"})
        cls.incoterm_id = cls.env.ref("account.incoterm_FCA")

    def _validate_picking(self, picking):
        """Helper to validate picking by setting quantities and validating."""
        for move in picking.move_ids:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()

    def get_po(self):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "date_planned": fields.Datetime.now(),
                "incoterm_id": self.incoterm_id.id,
                "order_line": [
                    Command.create(
                        {
                            "name": "Test Line",
                            "product_id": self.product.id,
                            "product_qty": 4.0,
                            "product_uom": self.product.uom_po_id.id,
                            "price_unit": 1,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )


class TestPurchaseContainer(TestPurchaseContainerBase):
    """Tests for core purchase container functionality."""

    def test_container_by_purchase(self):
        """Test container-purchase order relationships."""
        # first PO
        po = self.get_po()
        po.button_confirm()
        pick01 = po.picking_ids[0]
        pick01.container_id = self.cont_a.id
        self.assertIn(self.cont_a, po.container_ids)
        self.assertEqual(self.cont_a.purchase_order_count, 1)
        self._validate_picking(pick01)
        # this update triggers a new picking
        po.order_line[0].product_qty = 7
        pick02 = po.picking_ids.filtered(lambda x: x.state != "done")
        pick02.container_id = self.cont_b.id
        self._validate_picking(pick02)
        self.assertEqual(pick02.state, "done")
        self.assertIn(self.cont_b, po.container_ids)
        self.assertEqual(self.cont_b.purchase_order_count, 1)
        # second PO
        po2 = po.copy()
        po2.button_confirm()
        pick11 = po2.picking_ids
        pick11.container_id = self.cont_b.id
        self._validate_picking(pick11)
        self.assertIn(self.cont_b, po2.container_ids)
        self.assertEqual(pick11.state, "done")
        self.assertEqual(len(self.cont_b.purchase_order_ids), 2)
        self.assertEqual(self.cont_b.purchase_order_count, 1)
        # this method is not computed because not a stored field
        self.cont_b._compute_purchase_order_count()
        self.assertEqual(self.cont_b.purchase_order_count, 2)

        self.cont_b._compute_incoterm_id()
        self.assertEqual(self.cont_b.displayed_incoterm_id, self.incoterm_id)

    def test_action_views(self):
        """Test action view methods return proper actions."""
        po = self.get_po()
        po.button_confirm()
        pick01 = po.picking_ids[0]
        pick01.container_id = self.cont_a.id
        self.cont_a.action_view_rfq()
        self.cont_a.action_view_order()
        self.cont_a.action_view_picking()

    def test_container_code_uppercase(self):
        """Test that container code is converted to uppercase."""
        container = self.env["purchase.container"].create({"code": "test123"})
        self.assertEqual(container.code, "TEST123")

    def test_container_name_computation(self):
        """Test container name includes code and PO references."""
        po = self.get_po()
        po.button_confirm()
        pick = po.picking_ids[0]
        pick.container_id = self.cont_a.id
        self.cont_a.purchase_order_ids = [(4, po.id)]
        self.cont_a._compute_name()
        self.assertIn("AA", self.cont_a.name)
        self.assertIn(po.name, self.cont_a.name)


class TestContainerStateTransitions(TestPurchaseContainerBase):
    """Tests for container state transitions and actions."""

    def test_state_transitions(self):
        """Test state transition actions."""
        container = self.env["purchase.container"].create(
            {
                "code": "STATE-TEST",
                "state": "in_progress",
            }
        )
        self.assertEqual(container.state, "in_progress")

        # Test on_water transition
        container.action_set_on_water()
        self.assertEqual(container.state, "on_water")
        self.assertEqual(container.date_atd, date.today())

        # Test arrival notice transition
        container.action_set_arrival_notice()
        self.assertEqual(container.state, "arrival_notice")

        # Test delivered transition
        container.action_set_delivered()
        self.assertEqual(container.state, "delivered")
        self.assertEqual(container.date_delivered, date.today())

        # Test received transition
        container.action_set_received()
        self.assertEqual(container.state, "received")
        self.assertEqual(container.date_received, date.today())

    def test_container_lock_unlock(self):
        """Test container lock and unlock functionality."""
        container = self.env["purchase.container"].create({"code": "LOCK-TEST"})
        self.assertFalse(container.is_locked)

        container.button_lock()
        self.assertTrue(container.is_locked)

        container.button_unlock()
        self.assertFalse(container.is_locked)

    def test_ett_computation(self):
        """Test estimated transit time computation."""
        container = self.env["purchase.container"].create(
            {
                "code": "ETT-TEST",
                "date_etd": date.today(),
                "date_eta": date.today() + timedelta(days=30),
            }
        )
        container._compute_date_ett()
        # date_ett is a Char field, so it stores the timedelta as a string
        self.assertIn("30 days", container.date_ett)


class TestContainerFields(TestPurchaseContainerBase):
    """Tests for container field functionality."""

    def test_freight_forwarder_ref(self):
        """Test freight forwarder reference field."""
        container = self.env["purchase.container"].create(
            {
                "code": "FF-TEST",
                "freight_forwarder_ref": "B00064516",
            }
        )
        self.assertEqual(container.freight_forwarder_ref, "B00064516")

    def test_additional_fees_fields(self):
        """Test additional fees boolean and amount fields."""
        container = self.env["purchase.container"].create(
            {
                "code": "FEES-TEST",
                "has_additional_fees": True,
                "per_diem_fees": 150.00,
                "per_diem_reason": "Customs delay",
            }
        )
        self.assertTrue(container.has_additional_fees)
        self.assertEqual(container.per_diem_fees, 150.00)
        self.assertEqual(container.per_diem_reason, "Customs delay")

    def test_shipping_tracking_fields(self):
        """Test shipping and tracking fields."""
        carrier = self.env["res.partner"].create({"name": "Maersk Line"})
        container = self.env["purchase.container"].create(
            {
                "code": "TRACK-TEST",
                "carrier_id": carrier.id,
                "vessel_name": "MSC Oscar",
                "voyage_number": "VY2025001",
                "tracking_number": "MSKU1234567",
            }
        )
        self.assertEqual(container.carrier_id, carrier)
        self.assertEqual(container.vessel_name, "MSC Oscar")
        self.assertEqual(container.voyage_number, "VY2025001")
        self.assertEqual(container.tracking_number, "MSKU1234567")


class TestContainerTrackingUrl(TestPurchaseContainerBase):
    """Tests for tracking URL computation."""

    def test_tracking_url_maersk(self):
        """Test tracking URL generation for Maersk."""
        carrier = self.env["res.partner"].create({"name": "Maersk Line"})
        container = self.env["purchase.container"].create(
            {
                "code": "URL-MAERSK",
                "carrier_id": carrier.id,
                "tracking_number": "MSKU1234567",
            }
        )
        container._compute_tracking_url()
        self.assertIn("maersk.com", container.tracking_url)
        self.assertIn("MSKU1234567", container.tracking_url)

    def test_tracking_url_msc(self):
        """Test tracking URL generation for MSC."""
        carrier = self.env["res.partner"].create({"name": "MSC Mediterranean"})
        container = self.env["purchase.container"].create(
            {
                "code": "URL-MSC",
                "carrier_id": carrier.id,
                "tracking_number": "MSCU7654321",
            }
        )
        container._compute_tracking_url()
        self.assertIn("msc.com", container.tracking_url)

    def test_tracking_url_generic(self):
        """Test tracking URL generation for unknown carriers."""
        carrier = self.env["res.partner"].create({"name": "Unknown Carrier"})
        container = self.env["purchase.container"].create(
            {
                "code": "URL-GENERIC",
                "carrier_id": carrier.id,
                "tracking_number": "UNKN1234567",
            }
        )
        container._compute_tracking_url()
        self.assertIn("searates.com", container.tracking_url)

    def test_tracking_url_no_carrier(self):
        """Test tracking URL is empty without carrier."""
        container = self.env["purchase.container"].create(
            {
                "code": "URL-NONE",
                "tracking_number": "TEST1234567",
            }
        )
        container._compute_tracking_url()
        self.assertFalse(container.tracking_url)

    def test_action_open_tracking(self):
        """Test open tracking action returns URL action."""
        carrier = self.env["res.partner"].create({"name": "Maersk"})
        container = self.env["purchase.container"].create(
            {
                "code": "ACTION-TRACK",
                "carrier_id": carrier.id,
                "tracking_number": "MSKU1234567",
            }
        )
        container._compute_tracking_url()
        action = container.action_open_tracking()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertIn("maersk.com", action["url"])


class TestContainerDocuments(TestPurchaseContainerBase):
    """Tests for container document tracking."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create document types
        cls.doc_type_invoice = cls.env["container.document.type"].create(
            {
                "name": "Commercial Invoice",
                "required": True,
                "sequence": 10,
            }
        )
        cls.doc_type_packing = cls.env["container.document.type"].create(
            {
                "name": "Packing List",
                "required": True,
                "sequence": 20,
            }
        )
        cls.doc_type_cert = cls.env["container.document.type"].create(
            {
                "name": "Certificate of Origin",
                "required": False,
                "sequence": 30,
            }
        )

    def test_document_creation(self):
        """Test creating documents for a container."""
        container = self.env["purchase.container"].create({"code": "DOC-TEST"})
        doc = self.env["container.document"].create(
            {
                "container_id": container.id,
                "document_type_id": self.doc_type_invoice.id,
            }
        )
        self.assertEqual(doc.state, "missing")
        self.assertTrue(doc.required)
        self.assertEqual(doc.container_id, container)

    def test_document_state_workflow(self):
        """Test document state transitions."""
        container = self.env["purchase.container"].create({"code": "DOC-STATE"})
        doc = self.env["container.document"].create(
            {
                "container_id": container.id,
                "document_type_id": self.doc_type_invoice.id,
                "state": "missing",
            }
        )

        # Move to pending
        doc.state = "pending"
        doc.date_received = date.today()
        self.assertEqual(doc.state, "pending")

        # Approve
        doc.action_approve()
        self.assertEqual(doc.state, "approved")
        self.assertEqual(doc.date_approved, date.today())

        # Reset
        doc.action_reset()
        self.assertEqual(doc.state, "pending")
        self.assertFalse(doc.date_approved)

        # Reject
        doc.action_reject()
        self.assertEqual(doc.state, "rejected")

    def test_documents_complete_computation(self):
        """Test documents_complete field computation."""
        container = self.env["purchase.container"].create({"code": "DOC-COMPLETE"})

        # No documents - should be complete (no required docs to check)
        container._compute_documents_complete()
        self.assertTrue(container.documents_complete)

        # Add required document in missing state
        doc1 = self.env["container.document"].create(
            {
                "container_id": container.id,
                "document_type_id": self.doc_type_invoice.id,
                "state": "missing",
            }
        )
        container._compute_documents_complete()
        self.assertFalse(container.documents_complete)

        # Approve the document
        doc1.action_approve()
        container._compute_documents_complete()

        # Add another required document
        doc2 = self.env["container.document"].create(
            {
                "container_id": container.id,
                "document_type_id": self.doc_type_packing.id,
                "state": "missing",
            }
        )
        container._compute_documents_complete()
        self.assertFalse(container.documents_complete)

        # Approve second document
        doc2.action_approve()
        container._compute_documents_complete()
        self.assertTrue(container.documents_complete)

    def test_create_required_documents(self):
        """Test action to create required document records."""
        container = self.env["purchase.container"].create({"code": "DOC-CREATE"})
        self.assertEqual(len(container.document_ids), 0)

        container.action_create_required_documents()

        # Should have created records for required document types
        required_types = self.env["container.document.type"].search(
            [("required", "=", True)]
        )
        self.assertGreaterEqual(len(container.document_ids), len(required_types))

    def test_document_count(self):
        """Test document count computation."""
        container = self.env["purchase.container"].create({"code": "DOC-COUNT"})
        self.assertEqual(container.document_count, 0)

        self.env["container.document"].create(
            {
                "container_id": container.id,
                "document_type_id": self.doc_type_invoice.id,
            }
        )
        container._compute_document_count()
        self.assertEqual(container.document_count, 1)

        self.env["container.document"].create(
            {
                "container_id": container.id,
                "document_type_id": self.doc_type_packing.id,
            }
        )
        container._compute_document_count()
        self.assertEqual(container.document_count, 2)

    def test_action_view_documents(self):
        """Test action to view documents."""
        container = self.env["purchase.container"].create({"code": "DOC-VIEW"})
        action = container.action_view_documents()
        self.assertEqual(action["res_model"], "container.document")
        # Domain is [('container_id', '=', container.id)]
        self.assertEqual(action["domain"][0][2], container.id)


class TestContainerLines(TestPurchaseContainerBase):
    """Tests for container line functionality."""

    def test_line_creation(self):
        """Test creating container lines."""
        container = self.env["purchase.container"].create({"code": "LINE-TEST"})
        line = self.env["container.line"].create(
            {
                "container_id": container.id,
                "product_id": self.product.id,
                "quantity": 100,
            }
        )
        self.assertEqual(line.container_id, container)
        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.quantity, 100)

    def test_line_carton_calculation(self):
        """Test quantity calculation from carton info."""
        container = self.env["purchase.container"].create({"code": "LINE-CARTON"})
        line = self.env["container.line"].create(
            {
                "container_id": container.id,
                "product_id": self.product.id,
                "quantity": 0,
                "carton_qty": 10,
                "units_per_carton": 50,
            }
        )
        line._onchange_carton_info()
        self.assertEqual(line.quantity, 500)

    def test_line_count(self):
        """Test line count computation."""
        container = self.env["purchase.container"].create({"code": "LINE-COUNT"})
        self.assertEqual(container.line_count, 0)

        self.env["container.line"].create(
            {
                "container_id": container.id,
                "product_id": self.product.id,
                "quantity": 100,
            }
        )
        container._compute_line_count()
        self.assertEqual(container.line_count, 1)

    def test_action_view_lines(self):
        """Test action to view lines."""
        container = self.env["purchase.container"].create({"code": "LINE-VIEW"})
        action = container.action_view_lines()
        self.assertEqual(action["res_model"], "container.line")
        # Domain is [('container_id', '=', container.id)]
        self.assertEqual(action["domain"][0][2], container.id)

    def test_line_product_onchange(self):
        """Test product onchange sets defaults."""
        container = self.env["purchase.container"].create({"code": "LINE-ONCHANGE"})
        line = self.env["container.line"].create(
            {
                "container_id": container.id,
                "product_id": self.product.id,
                "quantity": 1,
            }
        )
        line._onchange_product_id()
        self.assertEqual(
            line.product_uom_id, self.product.uom_po_id or self.product.uom_id
        )


class TestContainerType(TransactionCase):
    """Tests for container type model."""

    def test_container_types_exist(self):
        """Test that default container types are loaded."""
        types = self.env["container.type"].search([])
        type_names = types.mapped("name")
        self.assertIn("20'", type_names)
        self.assertIn("40'", type_names)
        self.assertIn("40' HC", type_names)
