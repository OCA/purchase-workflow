# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import SUPERUSER_ID
from odoo.tests.common import TransactionCase


class TestPurchaseRequestEmployee(TransactionCase):
    def setUp(self):
        super().setUp()
        self.purchase_request_obj = self.env["purchase.request"]
        self.wiz = self.env["purchase.request.line.make.purchase.order"]
        self.employee1 = self.env.ref("hr.employee_hne")
        self.employee2 = self.env.ref("hr.employee_mit")

    def test_purchase_request_employee(self):
        # Test 1: Check that the field 'requested_employee_ids' of a purchase order
        # created from a purchase request with the field 'requested_employee_id'
        # defined is populated correctly.
        vals = {
            "requested_by": SUPERUSER_ID,
            "requested_employee_id": self.employee1.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.env.ref("product.product_product_6").id,
                        "product_uom_id": self.env.ref("uom.product_uom_dozen").id,
                        "product_qty": 1.0,
                    },
                )
            ],
        }
        purchase_request1 = self.purchase_request_obj.create(vals)
        purchase_request1.button_approved()

        wiz_vals = {"supplier_id": self.env.ref("base.res_partner_1").id}
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=purchase_request1.mapped("line_ids").ids,
        ).create(wiz_vals)
        wiz_id.make_purchase_order()

        self.assertListEqual(
            purchase_request1.mapped(
                "line_ids.purchase_lines.order_id.requested_employee_ids"
            ).ids,
            self.env.ref("hr.employee_hne").ids,
            "Should be the same employee",
        )

        # Test 2: Check that the field 'requested_employee_ids' of a purchase order
        # created from two different purchase request with different employees defined
        # in field 'requested_employee_id' is populated correctly.
        vals["requested_employee_id"] = self.employee2.id
        purchase_request2 = self.purchase_request_obj.create(vals)
        purchase_request2.button_approved()

        wiz_vals = {
            "supplier_id": self.env.ref("base.res_partner_1").id,
            "purchase_order_id": purchase_request1.mapped(
                "line_ids.purchase_lines.order_id"
            ).id,
        }
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=purchase_request2.mapped("line_ids").ids,
        ).create(wiz_vals)
        wiz_id.make_purchase_order()

        employees = self.employee1 | self.employee2
        self.assertListEqual(
            purchase_request2.mapped(
                "line_ids.purchase_lines.order_id.requested_employee_ids"
            ).ids,
            employees.ids,
            "Should be the same employees",
        )
