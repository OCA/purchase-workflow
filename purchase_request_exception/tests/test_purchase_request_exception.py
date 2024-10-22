# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.addons.purchase_request.tests.common import TestPurchaseRequestBase


class TestPurchaseRequestException(TestPurchaseRequestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Useful models
        cls.date_required = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        cls.purchase_request_exception_confirm = cls.env[
            "purchase.request.exception.confirm"
        ]
        cls.exception_noapprover = cls.env.ref(
            "purchase_request_exception.pr_excep_no_approver"
        )
        cls.exception_qtycheck = cls.env.ref(
            "purchase_request_exception.prl_excep_qty_check"
        )
        cls.pr_vals = {
            "requested_by": cls.user.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Pen",
                        "product_qty": 5.0,
                        "estimated_cost": 500.0,
                        "date_required": cls.date_required,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "Ink",
                        "product_qty": 5.0,
                        "estimated_cost": 250.0,
                        "date_required": cls.date_required,
                    },
                ),
            ],
        }

    def test_purchase_request_exception(self):
        self.exception_noapprover.active = True
        self.exception_qtycheck.active = True
        self.pr = self.purchase_request_obj.create(self.pr_vals.copy())

        # confirm
        self.pr.button_to_approve()
        self.assertEqual(self.pr.state, "draft")
        # test all draft pr
        self.pr2 = self.purchase_request_obj.create(self.pr_vals.copy())

        self.purchase_request_obj.test_all_draft_requests()
        self.assertEqual(self.pr2.state, "draft")
        # Set ignore_exception flag  (Done after ignore is selected at wizard)
        self.pr.ignore_exception = True
        self.pr.button_to_approve()
        self.assertEqual(self.pr.state, "to_approve")

        # Add a request line to test after PR is confirmed
        # set ignore_exception = False  (Done by onchange of line_ids)
        field_onchange = self.purchase_request_obj._onchange_spec()
        self.assertEqual(field_onchange.get("line_ids"), "1")
        self.env.cache.invalidate()
        self.pr3New = self.purchase_request_obj.new(self.pr_vals.copy())
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
        self.pr.button_to_approve()
        self.pr.with_user(self.manager_user).button_rejected()
        self.pr.button_draft()
        self.assertEqual(self.pr.state, "draft")
        self.assertTrue(not self.pr.ignore_exception)

        # Simulation the opening of the wizard purchase_request_exception_confirm and
        # set ignore_exception to True
        pr_except_confirm = self.purchase_request_exception_confirm.with_context(
            active_id=self.pr.id,
            active_ids=[self.pr.id],
            active_model=self.pr._name,
        ).create({"ignore": True})
        pr_except_confirm.action_confirm()
        self.assertTrue(self.pr.ignore_exception)
