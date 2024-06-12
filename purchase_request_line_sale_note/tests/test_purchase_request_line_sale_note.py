# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form, SavepointCase


class TestPurchaseRequestLineSaleNote(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.product.purchase_request = True
        cls.mto_route = cls.env.ref("stock.route_warehouse0_mto")
        cls.mto_route.active = True
        cls.sale_note = "Custom sale note"

    @classmethod
    def _create_sale_order(cls):
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        with sale_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = 100
            line_form.route_id = cls.mto_route
            line_form.note = cls.sale_note
        return sale_form.save()

    def test_purchase_request_line_note(self):
        sale = self._create_sale_order()
        sale.action_confirm()
        purchase_request = self.env["purchase.request"].search(
            [("origin", "=", sale.name)]
        )
        purchase_request_line = purchase_request.line_ids
        self.assertEqual(purchase_request_line.specifications, self.sale_note)
        purchase_request.button_to_approve()
        purchase_request.button_approved()
        create_rfq_wiz_form = Form(
            self.env["purchase.request.line.make.purchase.order"].with_context(
                active_model="purchase.request", active_ids=purchase_request.ids
            )
        )
        create_rfq_wiz = create_rfq_wiz_form.save()
        create_rfq_wiz.make_purchase_order()
        purchase_order_line = purchase_request_line.purchase_lines
        self.assertEqual(purchase_order_line.sale_note, self.sale_note)
