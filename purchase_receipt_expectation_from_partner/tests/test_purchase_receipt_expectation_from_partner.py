# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tests.common import Form

from odoo.addons.purchase_receipt_expectation.tests.test_purchase_receipt_expectation import (
    TestPurchaseReceiptExpectation,
)


class TestPurchaseReceiptExpectationFromPartner(TestPurchaseReceiptExpectation):
    def test_00_receipt_expectation_from_partner(self):
        """Tests receipt expectation being taken from PO partner

        Steps:
            - Extend `purchase.order` with a mock-up model
            - Extend `receipt_expectation` with a mock-up value "test"
            - Check `res.partner.receipt_expectation` selection values
            - Update test partner `receipt_expectation` with value "test"
            - Create a new PO with given partner
            - Check PO `receipt_expectation`

        Expect:
            - `res.partner.receipt_expectation` selection values contain "test"
            - PO `receipt_expectation` is "test"
        """

        class PurchaseOrderMockUp(models.Model):
            _inherit = "purchase.order"

            receipt_expectation = fields.Selection(
                selection_add=[("test", "Test")],
                ondelete={"test": "set default"},
            )

        PurchaseOrderMockUp._build_model(self.registry, self.cr)
        self.registry.setup_models(self.cr)

        self.assertIn(
            "test",
            self.env["res.partner"]._fields["receipt_expectation"].get_values(self.env),
        )
        self.po_partner.receipt_expectation = "test"
        with Form(self.env["purchase.order"]) as po_form:
            po_form.partner_id = self.po_partner
        po = po_form.save()
        self.assertEqual(po.receipt_expectation, "test")
