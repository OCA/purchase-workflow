# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestPurchaseRequestException(TransactionCase):
    def setUp(self):
        super(TestPurchaseRequestException, self).setUp()
        # Useful models
        self.PurchaseRequest = self.env["purchase.request"]
        self.PurchaseRequestLine = self.env["purchase.request.line"]
        self.request_user_id = self.env.ref("base.user_admin")
        self.date_required = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.purchase_request_exception_confirm = self.env[
            "purchase.request.exception.confirm"
        ]
        self.exception_noapprover = self.env.ref(
            "purchase_request_exception.pr_excep_no_approver"
        )
        self.exception_qtycheck = self.env.ref(
            "purchase_request_exception.prl_excep_qty_check"
        )
        self.pr_vals = {
            "requested_by": self.request_user_id.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Pen",
                        "product_qty": 5.0,
                        "estimated_cost": 500.0,
                        "date_required": self.date_required,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "Ink",
                        "product_qty": 5.0,
                        "estimated_cost": 250.0,
                        "date_required": self.date_required,
                    },
                ),
            ],
        }

    def test_purchase_request_exception(self):
        self.exception_noapprover.active = True
        self.exception_qtycheck.active = True
        self.pr = self.PurchaseRequest.create(self.pr_vals.copy())

        # confirm
        self.pr.button_to_approve()
        self.assertEqual(self.pr.state, "draft")
        # test all draft pr
        self.pr2 = self.PurchaseRequest.create(self.pr_vals.copy())

        self.PurchaseRequest.test_all_draft_requests()
        self.assertEqual(self.pr2.state, "draft")
        # Set ignore_exception flag  (Done after ignore is selected at wizard)
        self.pr.ignore_exception = True
        self.pr.button_to_approve()
        self.assertEqual(self.pr.state, "to_approve")

        # Add a request line to test after PR is confirmed
        # set ignore_exception = False  (Done by onchange of line_ids)
        field_onchange = self.PurchaseRequest._onchange_spec()
        self.assertEqual(field_onchange.get("line_ids"), "1")
        self.env.cache.invalidate()
        self.pr3New = self.PurchaseRequest.new(self.pr_vals.copy())
        self.pr3New.ignore_exception = True
        self.pr3New.state = "to_approve"
        self.pr3New.onchange_ignore_exception()
        self.assertFalse(self.pr3New.ignore_exception)
        self.pr.write(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Pencil",
                            "product_qty": 2.0,
                            "estimated_cost": 30.0,
                            "date_required": self.date_required,
                        },
                    )
                ]
            }
        )

        # Set ignore exception True  (Done manually by user)
        self.pr.ignore_exception = True
        self.pr.button_rejected()
        self.pr.button_draft()
        self.assertEqual(self.pr.state, "draft")
        self.assertTrue(not self.pr.ignore_exception)

        # Simulation the opening of the wizard purchase_request_exception_confirm and
        # set ignore_exception to True
        pr_except_confirm = self.purchase_request_exception_confirm.with_context(
            {
                "active_id": self.pr.id,
                "active_ids": [self.pr.id],
                "active_model": self.pr._name,
            }
        ).create({"ignore": True})
        pr_except_confirm.action_confirm()
        self.assertTrue(self.pr.ignore_exception)
