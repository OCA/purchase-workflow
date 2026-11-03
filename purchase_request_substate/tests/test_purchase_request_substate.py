# Copyright 2021 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBaseSubstate(TransactionCase):
    def setUp(self):
        super(TestBaseSubstate, self).setUp()
        # Prepare PR
        self.purchase_request_obj = self.env["purchase.request"]
        self.purchase_request_line_obj = self.env["purchase.request.line"]
        self.wiz = self.env["purchase.request.line.make.purchase.order"]
        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        self.pr_test = self.purchase_request_obj.create(vals)
        vals = {
            "request_id": self.pr_test.id,
            "product_id": self.env.ref("product.product_product_13").id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 5.0,
        }
        self.purchase_request_line_obj.create(vals)

        # Prepare states
        self.substate_to_verify = self.env.ref(
            "purchase_request_substate.base_substate_to_verify"
        )
        self.substate_checked = self.env.ref(
            "purchase_request_substate.base_substate_checked"
        )
        self.substate_verified = self.env.ref(
            "purchase_request_substate.base_substate_verified"
        )
        # Active substate
        (
            self.substate_to_verify + self.substate_checked + self.substate_verified
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
