# Copyright 2019 Akretion Mourad EL HADJ MIMOUNE
# Copyright 2020 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBaseSubstate(TransactionCase):
    def setUp(self):
        super(TestBaseSubstate, self).setUp()
        self.substate_test_purchase = self.env["purchase.order"]
        self.substate_test_purchase_line = self.env["purchase.order.line"]

        self.substate_under_nego = self.env.ref(
            "purchase_substate.base_substate_under_nego"
        )
        self.substate_won = self.env.ref("purchase_substate.base_substate_won")
        self.substate_wait_docs = self.env.ref(
            "purchase_substate.base_substate_wait_docs"
        )
        self.substate_valid_docs = self.env.ref(
            "purchase_substate.base_substate_valid_docs"
        )
        self.substate_in_receipt = self.env.ref(
            "purchase_substate.base_substate_in_receipt"
        )

        self.product = self.env["product.product"].create({"name": "Test"})

    def test_purchase_order_substate(self):
        partner = self.env.ref("base.res_partner_1")
        po_test1 = self.substate_test_purchase.create(
            {
                "name": "Test base substate to basic purchase",
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "line test",
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_po_id.id,
                            "price_unit": 120.0,
                            "product_qty": 1.5,
                            "date_planned": fields.Date.today(),
                        },
                    )
                ],
            }
        )
        self.assertTrue(po_test1.state == "draft")
        self.assertTrue(po_test1.substate_id == self.substate_under_nego)

        # Block substate not corresponding to draft state
        with self.assertRaises(ValidationError):
            po_test1.substate_id = self.substate_valid_docs
        # Test that validation of purchase order change substate_id
        po_test1.button_confirm()
        self.assertTrue(po_test1.state == "purchase")
        self.assertTrue(po_test1.substate_id == self.substate_valid_docs)

        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        po_test1.button_cancel()
        self.assertTrue(po_test1.state == "cancel")
        self.assertTrue(not po_test1.substate_id)
