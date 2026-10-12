# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPurchaseOrderApproved(TransactionCase):
    def test_purchase_order_approved(self):
        partner = self.env["res.partner"].create(
            {"name": "Test Partner", "is_company": True}
        )
        po = self.env["purchase.order"].create({"partner_id": partner.id})
        po.button_confirm()
        po.button_release()
