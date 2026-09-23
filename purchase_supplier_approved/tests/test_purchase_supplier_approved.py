# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import timedelta

from odoo import exceptions, fields
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestPurchaseSupplierApproved(common.TransactionCase):
    """Test cases for Purchase Approved Suppliers module"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test users
        cls.group_purchase_user = cls.env.ref("purchase.group_purchase_user")
        cls.group_manage_approved = cls.env.ref(
            "purchase_supplier_approved.group_manage_approved_suppliers"
        )

        cls.purchase_user = cls.env["res.users"].create(
            {
                "name": "Purchase User",
                "login": "purchase_user",
                "email": "purchase_user@example.com",
                "groups_id": [(6, 0, [cls.group_purchase_user.id])],
            }
        )

        cls.approved_manager = cls.env["res.users"].create(
            {
                "name": "Approved Manager",
                "login": "approved_manager",
                "email": "approved_manager@example.com",
                "groups_id": [
                    (6, 0, [cls.group_purchase_user.id, cls.group_manage_approved.id])
                ],
            }
        )

        # Create test suppliers
        cls.supplier1 = cls.env["res.partner"].create(
            {
                "name": "Test Supplier 1",
                "is_company": True,
                "supplier_rank": 1,
            }
        )

        cls.supplier2 = cls.env["res.partner"].create(
            {
                "name": "Test Supplier 2",
                "is_company": True,
                "supplier_rank": 1,
            }
        )

        # Create test product categories
        cls.category_components = cls.env["product.category"].create(
            {
                "name": "Components",
                "require_approved_supplier": True,
            }
        )

        cls.category_services = cls.env["product.category"].create(
            {
                "name": "Services",
                "require_approved_supplier": False,
            }
        )

        # Create test products
        cls.product_component = cls.env["product.template"].create(
            {
                "name": "Test Component",
                "categ_id": cls.category_components.id,
                "purchase_ok": True,
            }
        )

        cls.product_service = cls.env["product.template"].create(
            {
                "name": "Test Service",
                "categ_id": cls.category_services.id,
                "purchase_ok": True,
            }
        )

        cls.product_exception = cls.env["product.template"].create(
            {
                "name": "Test Exception Product",
                "categ_id": cls.category_services.id,
                "approved_supplier_requirement": "required",
                "purchase_ok": True,
            }
        )

    def _create_purchase_order(self, partner, product, user=None, qty=1.0, price=100.0):
        """Helper method to create a test purchase order"""
        order_data = {
            "partner_id": partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": product.product_variant_ids[0].id,
                        "product_qty": qty,
                        "price_unit": price,
                    },
                )
            ],
        }

        if user:
            return self.env["purchase.order"].with_user(user).create(order_data)
        else:
            return self.env["purchase.order"].create(order_data)

    def test_user_permissions(self):
        """Test that users have correct permissions"""
        # Purchase user should not be able to see approved supplier fields
        self.assertFalse(
            self.purchase_user.has_group(
                "purchase_supplier_approved.group_manage_approved_suppliers"
            )
        )

        # Approved manager should be able to see approved supplier fields
        self.assertTrue(
            self.approved_manager.has_group(
                "purchase_supplier_approved.group_manage_approved_suppliers"
            )
        )

    def test_category_configuration(self):
        """Test product category configuration"""
        # Components category should require approved suppliers
        self.assertTrue(self.category_components.require_approved_supplier)

        # Services category should not require approved suppliers
        self.assertFalse(self.category_services.require_approved_supplier)

    def test_product_exception_configuration(self):
        """Test product exception configuration"""
        # Component product should follow category (require approval)
        self.assertTrue(self.product_component.is_approved_supplier_required)

        # Service product should follow category (no approval required)
        self.assertFalse(self.product_service.is_approved_supplier_required)

        # Exception product should override category (require approval)
        self.assertTrue(self.product_exception.is_approved_supplier_required)

    def test_supplier_approval_check(self):
        """Test supplier approval validation"""
        # Create approved supplier
        self.env["purchase.supplier.approved"].with_user(self.approved_manager).create(
            {
                "partner_id": self.supplier1.id,
                "product_tmpl_id": self.product_component.id,
                "date_from": fields.Date.today(),
            }
        )

        # Check that supplier is approved
        self.assertTrue(self.product_component.is_supplier_approved(self.supplier1.id))

        # Check that different supplier is not approved
        self.assertFalse(self.product_component.is_supplier_approved(self.supplier2.id))

        # Check product that doesn't require approval
        self.assertTrue(self.product_service.is_supplier_approved(self.supplier2.id))

    def test_purchase_order_validation_warning(self):
        """Test purchase order validation warnings"""
        # Create PO with unapproved supplier for product that requires approval
        po = self._create_purchase_order(
            self.supplier2, self.product_component, self.purchase_user
        )

        # PO should have unapproved supplier
        self.assertTrue(po.has_unapproved_supplier)

        # Check warning on change
        po.with_user(self.purchase_user)._onchange_check_supplier_approval()

        # Should not be able to confirm without override
        with self.assertRaises(exceptions.UserError):
            po.with_user(self.purchase_user).button_confirm()

    def test_purchase_order_override(self):
        """Test purchase order override mechanism"""
        # Create PO with unapproved supplier
        po = self._create_purchase_order(
            self.supplier2, self.product_component, self.approved_manager
        )

        # Should be able to confirm with override
        po.override_reason = "Urgent order - approval pending"
        po.override_supplier_approval = True
        po.button_confirm()

        self.assertEqual(po.state, "purchase")

    def test_purchase_order_no_validation_required(self):
        """Test PO for products that don't require approval"""
        # Create PO for service product (no approval required)
        po = self._create_purchase_order(
            self.supplier2, self.product_service, self.purchase_user
        )

        # PO should not have unapproved supplier
        self.assertFalse(po.has_unapproved_supplier)

        # Should be able to confirm without override
        po.button_confirm()
        self.assertEqual(po.state, "purchase")

    def test_smart_buttons_product_template(self):
        """Test smart button on product template"""
        # Create approved supplier
        self.env["purchase.supplier.approved"].with_user(self.approved_manager).create(
            {
                "partner_id": self.supplier1.id,
                "product_tmpl_id": self.product_component.id,
                "date_from": fields.Date.today(),
            }
        )

        # Check smart button count
        self.assertEqual(self.product_component.approved_supplier_count, 1)

        # Test smart button action
        action = self.product_component.action_view_approved_suppliers()
        self.assertEqual(action["res_model"], "purchase.supplier.approved")
        self.assertEqual(
            action["domain"], [("product_tmpl_id", "=", self.product_component.id)]
        )

    def test_smart_buttons_partner(self):
        """Test smart button on partner"""
        # Create approved supplier
        self.env["purchase.supplier.approved"].with_user(self.approved_manager).create(
            {
                "partner_id": self.supplier1.id,
                "product_tmpl_id": self.product_component.id,
                "date_from": fields.Date.today(),
            }
        )

        # Check smart button count
        self.assertEqual(self.supplier1.approved_product_count, 1)

        # Test smart button action
        action = self.supplier1.action_view_approved_products()
        self.assertEqual(action["res_model"], "purchase.supplier.approved")
        self.assertEqual(action["domain"], [("partner_id", "=", self.supplier1.id)])

    def test_date_validity(self):
        """Test date validity in supplier approval"""
        # Create approved supplier with future date
        future_date = fields.Date.today() + timedelta(days=30)
        self.env["purchase.supplier.approved"].with_user(self.approved_manager).create(
            {
                "partner_id": self.supplier1.id,
                "product_tmpl_id": self.product_component.id,
                "date_from": future_date,
            }
        )

        # Should not be approved today
        self.assertFalse(
            self.product_component.is_supplier_approved(
                self.supplier1.id, fields.Date.today()
            )
        )

        # Should be approved on future date
        self.assertTrue(
            self.product_component.is_supplier_approved(self.supplier1.id, future_date)
        )

    def test_inactive_approval(self):
        """Test that inactive approvals are not considered"""
        # Create inactive approved supplier
        self.env["purchase.supplier.approved"].with_user(self.approved_manager).create(
            {
                "partner_id": self.supplier1.id,
                "product_tmpl_id": self.product_component.id,
                "date_from": fields.Date.today(),
                "active": False,
            }
        )

        # Should not be approved since it's inactive
        self.assertFalse(self.product_component.is_supplier_approved(self.supplier1.id))

    def test_line_level_computed_field(self):
        """Test line-level computed field"""
        # Create approved supplier
        self.env["purchase.supplier.approved"].with_user(self.approved_manager).create(
            {
                "partner_id": self.supplier1.id,
                "product_tmpl_id": self.product_component.id,
                "date_from": fields.Date.today(),
            }
        )

        # Create PO with approved supplier
        po_approved = self._create_purchase_order(
            self.supplier1, self.product_component, self.purchase_user
        )

        # Create PO with unapproved supplier
        po_unapproved = self._create_purchase_order(
            self.supplier2, self.product_component, self.purchase_user
        )

        # Check line-level computed field
        self.assertFalse(po_approved.order_line[0].has_unapproved_supplier)
        self.assertTrue(po_unapproved.order_line[0].has_unapproved_supplier)

        # Check order-level computed field
        self.assertFalse(po_approved.has_unapproved_supplier)
        self.assertTrue(po_unapproved.has_unapproved_supplier)
