# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestPurchaseOrderMassCancel(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase = cls.env["purchase.order"].search([("state", "=", "draft")])
        cls.wizard = (
            cls.env["purchase.order.mass.cancel"]
            .with_context(active_ids=cls.purchase.ids)
            .create({})
        )

    def test_mass_cancel(self):
        all_state = all(state == "draft" for state in self.purchase.mapped("state"))
        self.assertTrue(all_state)
        self.wizard.confirm_cancel()
        all_state = all(state == "cancel" for state in self.purchase.mapped("state"))
        self.assertTrue(all_state)
