# Copyright 2021 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPurchaseRequestSubstate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Prepare PR
        cls.purchase_request_obj = cls.env["purchase.request"]
        cls.purchase_request_line_obj = cls.env["purchase.request.line"]
        cls.wiz = cls.env["purchase.request.line.make.purchase.order"]
        vals = {
            "picking_type_id": cls.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        cls.pr_test = cls.purchase_request_obj.create(vals)
        vals = {
            "request_id": cls.pr_test.id,
            "product_id": cls.env.ref("product.product_product_13").id,
            "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
            "product_qty": 5.0,
        }
        cls.purchase_request_line_obj.create(vals)

        # Prepare states
        cls.substate_to_verify = cls.env.ref(
            "purchase_request_substate.base_substate_to_verify"
        )
        cls.substate_checked = cls.env.ref(
            "purchase_request_substate.base_substate_checked"
        )
        cls.substate_verified = cls.env.ref(
            "purchase_request_substate.base_substate_verified"
        )
        # Active substate
        (
            cls.substate_to_verify + cls.substate_checked + cls.substate_verified
        ).active = True

    def test_purchase_request_order_substate(self):
        self.assertTrue(self.pr_test.state == "draft")
        self.assertTrue(not self.pr_test.substate_id)

        # Block substate not corresponding to draft state
        with self.assertRaises(ValidationError):
            self.pr_test.substate_id = self.substate_to_verify
        # Test that validation of purchase_request order change substate_id
        self.pr_test.button_to_approve()
        self.assertTrue(self.pr_test.state == "to_approve")
        self.assertTrue(self.pr_test.substate_id == self.substate_to_verify)

        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        self.pr_test.button_approved()
        self.assertTrue(self.pr_test.state == "approved")
        self.assertTrue(not self.pr_test.substate_id)
