# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPurchaseOrderApproved(TransactionCase):
    def test_purchase_order_approved(self):
        po = self.env["purchase.order"].create(
            {"partner_id": self.env.ref("base.res_partner_12").id}
        )
        po.button_confirm()
        po.button_release()
