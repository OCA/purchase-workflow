# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestPurchaseOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        cls.supplier = cls.env.ref("base.res_partner_1")
        vals = {
            "name": "PO TEST",
            "partner_id": cls.supplier.id,
        }
        cls.purchase_order = cls.env["purchase.order"].create(vals)
        product = cls.env.ref("product.product_product_4")
        cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": product.id,
                "date_planned": fields.Datetime.now(),
                "name": "Test",
                "product_qty": 10.0,
                "product_uom": product.uom_id.id,
                "price_unit": 100.0,
            }
        )

    def test_01(self):
        """
        Data:
            * one draft PO
            * supplier configured with purchase request second approval based
            on company policy
            * company configured with purchase_approve_active set to False
        Test Case:
            * confirm the PO
        Expected result:
            * PO is in state 'purchase'
        """
        self.assertEqual(self.purchase_order.state, "draft")
        self.purchase_order.company_id.purchase_approve_active = False
        self.supplier.purchase_requires_second_approval = "based_on_company"
        self.purchase_order.button_approve()
        self.assertEqual(self.purchase_order.state, "purchase")

    def test_02(self):
        """
        Data:
            * one draft PO
            * supplier configured with purchase request second approval based
            on company policy
            * company configured with purchase_approve_active set to True
        Test Case:
            * confirm the PO
        Expected result:
            * PO is in state 'approved'
        """
        self.assertEqual(self.purchase_order.state, "draft")
        self.purchase_order.company_id.purchase_approve_active = True
        self.supplier.purchase_requires_second_approval = "based_on_company"
        self.purchase_order.button_approve()
        self.assertEqual(self.purchase_order.state, "approved")

    def test_03(self):
        """
        Data:
            * one draft PO
            * supplier configured with purchase request second approval based
            set to 'never'
            * company configured with purchase_approve_active set to True
        Test Case:
            * confirm the PO
        Expected result:
            * PO is in state 'purchase'
        """
        self.assertEqual(self.purchase_order.state, "draft")
        self.purchase_order.company_id.purchase_approve_active = True
        self.supplier.purchase_requires_second_approval = "never"
        self.purchase_order.button_approve()
        self.assertEqual(self.purchase_order.state, "purchase")

    def test_04(self):
        """
        Data:
            * one draft PO
            * supplier configured with purchase request second approval based
            set to 'always'
            * company configured with purchase_approve_active set to False
        Test Case:
            * confirm the PO
        Expected result:
            * PO is in state 'approved'
        """
        self.assertEqual(self.purchase_order.state, "draft")
        self.purchase_order.company_id.purchase_approve_active = False
        self.supplier.purchase_requires_second_approval = "always"
        self.purchase_order.button_approve()
        self.assertEqual(self.purchase_order.state, "approved")

    def test_05(self):
        """
        Data:
            * one draft PO
            * supplier configured with purchase request second approval based
            set to 'always'
            * company configured with purchase_approve_active set to False
        Test Case:
            * confirm the PO
        Expected result:
            * PO is in state 'approved'
        """
        self.assertEqual(self.purchase_order.state, "draft")
        self.purchase_order.company_id.purchase_approve_active = False
        self.supplier.purchase_requires_second_approval = "always"
        self.purchase_order.button_approve()
        self.assertEqual(self.purchase_order.state, "approved")

    def test_06(self):
        """
        Data:
            * one draft PO (amount_total = 1000)
            * supplier configured with purchase request second approval
            set to 'always'
            * company configured with two-step validation and a low threshold
            * a purchase user (not a manager) and a purchase manager
        Test Case:
            * purchase user confirms the PO (goes to 'to approve')
            * manager approves the PO (goes to 'approved')
            * purchase user releases the PO via button_release
        Expected result:
            * PO is in state 'purchase' because _approval_allowed returns
              True for 'approved' state
        """
        purchase_user = self.env["res.users"].create(
            {
                "name": "Purchase User",
                "login": "purchase_user_test",
                "groups_id": [
                    (
                        6,
                        0,
                        [self.env.ref("purchase.group_purchase_user").id],
                    )
                ],
            }
        )
        self.purchase_order.company_id.po_double_validation = "two_step"
        self.purchase_order.company_id.po_double_validation_amount = 0.0
        self.supplier.purchase_requires_second_approval = "always"
        # Purchase user confirms → PO goes to 'to approve'
        self.purchase_order.with_user(purchase_user).button_confirm()
        self.assertEqual(self.purchase_order.state, "to approve")
        # Manager approves → PO goes to 'approved' (two-step from module)
        self.purchase_order.button_approve()
        self.assertEqual(self.purchase_order.state, "approved")
        # Purchase user releases → PO goes to 'purchase'
        self.purchase_order.with_user(purchase_user).button_release()
        self.assertEqual(self.purchase_order.state, "purchase")
