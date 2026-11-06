# Copyright 2021 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseRequestSubstate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Prepare PR
        cls.purchase_request_obj = cls.env["purchase.request"]
        cls.purchase_request_line_obj = cls.env["purchase.request.line"]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
            }
        )
        cls.substate_type = cls.env.ref(
            "purchase_request_substate.base_substate_type_purchase_request"
        )
        cls.target_state_value_to_approve = cls.env.ref(
            "purchase_request_substate.target_state_value_to_approve"
        )
        cls.substate_to_verify = cls.env["base.substate"].create(
            {
                "name": "To Verify",
                "sequence": 1,
                "target_state_value_id": cls.target_state_value_to_approve.id,
                "active": True,
            }
        )
        cls.substate_checked = cls.env["base.substate"].create(
            {
                "name": "Checked",
                "sequence": 2,
                "target_state_value_id": cls.target_state_value_to_approve.id,
                "active": True,
            }
        )
        cls.substate_verified = cls.env["base.substate"].create(
            {
                "name": "Verified",
                "sequence": 3,
                "target_state_value_id": cls.target_state_value_to_approve.id,
                "active": True,
            }
        )
        vals = {
            "picking_type_id": cls.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        cls.pr_test = cls.purchase_request_obj.create(vals)
        cls.purchase_request_line_obj.create(
            {
                "request_id": cls.pr_test.id,
                "product_id": cls.product.id,
                "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
                "product_qty": 5.0,
            }
        )

    def test_purchase_request_order_substate(self):
        self.assertEqual(self.pr_test.state, "draft")
        self.assertFalse(self.pr_test.substate_id)

        # Block substate not corresponding to draft state
        with self.assertRaises(ValidationError):
            self.pr_test.substate_id = self.substate_to_verify
        # Test that validation of purchase_request order change substate_id
        self.pr_test.button_to_approve()
        self.assertEqual(self.pr_test.state, "to_approve")
        self.assertEqual(self.pr_test.substate_id, self.substate_to_verify)

        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        self.pr_test.button_approved()
        self.assertEqual(self.pr_test.state, "approved")
        self.assertFalse(self.pr_test.substate_id)
