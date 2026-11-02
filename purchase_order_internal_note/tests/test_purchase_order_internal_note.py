# Copyright 2026 360ERP (<https://360ERP.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestPurchaseOrderInternalNote(BaseCommon):
    # Since 20.0, BaseCommon runs the tests with a new user that has only
    # these groups. A purchase user is needed to create purchase orders.
    _test_user_groups = ("base.group_user", "purchase.group_purchase_user")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "standard_price": 10.0}
        )
        cls.note = "Secret note for the purchase team only"

    def _create_order(self):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = self.vendor
        with order_form.order_line.new() as line:
            line.product_id = self.product
            line.product_qty = 1.0
        order_form.internal_note = self.note
        return order_form.save()

    def test_internal_note_in_form(self):
        order = self._create_order()
        self.assertEqual(order.internal_note, self.note)

    def test_internal_note_not_in_report(self):
        order = self._create_order()
        for report in (
            "purchase.report_purchaseorder",
            "purchase.report_purchasequotation",
        ):
            html = self.env["ir.actions.report"]._render_qweb_html(report, order.ids)[0]
            self.assertNotIn(self.note, html.decode())
