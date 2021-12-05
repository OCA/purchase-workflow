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
        cls.purchase_order.refresh()

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
