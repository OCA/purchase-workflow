# Copyright 2022 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestPurchaseWorkAcceptanceCancelConfirm(TransactionCase):
    def setUp(self):
        super(TestPurchaseWorkAcceptanceCancelConfirm, self).setUp()
        self.WorkAcceptance = self.env["work.acceptance"]

        self.partner = self.env.ref("base.res_partner_12")
        self.config_parameter = self.env.ref(
            "purchase_work_acceptance_cancel_confirm."
            "purchase_work_acceptance_cancel_confirm_disable"
        )

    def test_01_cancel_confirm_work_acceptance(self):
        """Cancel a document, I expect cancel_reason.
        Then, set to draft, I expect cancel_reason is deleted.
        """
        self.config_parameter.write({"value": "False"})
        self.work_acceptance = self.WorkAcceptance.create(
            {
                "partner_id": self.partner.id,
                "date_due": fields.Datetime.now(),
            }
        )
        # Click reject, cancel confirm wizard will open. Type in cancel_reason
        res = self.work_acceptance.button_cancel()
        ctx = res.get("context")
        self.assertEqual(ctx["cancel_method"], "button_cancel")
        self.assertEqual(ctx["default_has_cancel_reason"], "optional")
        wizard = Form(self.env["cancel.confirm"].with_context(ctx))
        wizard.cancel_reason = "Wrong information"
        wiz = wizard.save()
        # Confirm cancel on wizard
        wiz.confirm_cancel()
        self.assertEqual(self.work_acceptance.cancel_reason, wizard.cancel_reason)
        self.assertEqual(self.work_acceptance.state, "cancel")
        # Set to draft
        self.work_acceptance.button_draft()
        self.assertEqual(self.work_acceptance.cancel_reason, False)
        self.assertEqual(self.work_acceptance.state, "draft")
