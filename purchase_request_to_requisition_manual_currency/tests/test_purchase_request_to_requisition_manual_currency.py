# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form, TransactionCase


class TestPurchaseRequestManualCurrency(TransactionCase):
    def setUp(self):
        super().setUp()
        self.currency_eur = self.env.ref("base.EUR")
        self.currency_usd = self.env.ref("base.USD")
        self.main_company = self.env.ref("base.main_company")
        self.env.cr.execute(
            """UPDATE res_company SET currency_id = %s
            WHERE id = %s""",
            (self.currency_eur.id, self.main_company.id),
        )
        self.product1 = self.env.ref("product.product_product_7")
        self.wiz = self.env["purchase.request.line.make.purchase.requisition"]

    def _create_purchase_request(self, pr_lines):
        PurchaseRequest = self.env["purchase.request"]
        view_id = "purchase_request.view_purchase_request_form"
        with Form(PurchaseRequest, view=view_id) as pr:
            for pr_line in pr_lines:
                with pr.line_ids.new() as line:
                    line.product_id = pr_line["product_id"]
                    line.product_qty = pr_line["product_qty"]
                    line.estimated_cost = pr_line["estimated_cost"]
        purchase_request = pr.save()
        return purchase_request

    def test_01_purchase_request_manual_currency(self):
        purchase_request = self._create_purchase_request(
            [
                {
                    "product_id": self.product1,
                    "product_qty": 1,
                    "estimated_cost": 100,
                },
            ]
        )
        self.assertEqual(purchase_request.currency_id.name, "EUR")
        with Form(purchase_request) as pr:
            pr.currency_id = self.currency_usd
            pr.manual_currency = True
            pr.type_currency = "inverse_company_rate"
            pr.custom_rate = 100.0
        purchase_request.button_approved()
        self.assertEqual(purchase_request.state, "approved")
        purchase_request.button_approved()
        # Create wizard PR Line
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request.line_ids.id],
            active_id=purchase_request.line_ids.id,
        ).create({})
        wiz_id.make_purchase_requisition()
        # Check rate manual should send to TE
        self.assertEqual(
            purchase_request.line_ids.mapped(
                "requisition_lines.requisition_id"
            ).manual_currency,
            purchase_request.manual_currency,
        )
        self.assertEqual(
            purchase_request.line_ids.mapped(
                "requisition_lines.requisition_id"
            ).type_currency,
            purchase_request.type_currency,
        )
        self.assertEqual(
            purchase_request.line_ids.mapped(
                "requisition_lines.requisition_id"
            ).custom_rate,
            purchase_request.custom_rate,
        )

        # Test create TE from PR
        wiz_id = self.wiz.with_context(
            active_model="purchase.request",
            active_ids=[purchase_request.id],
        ).create({})
        wiz_id.make_purchase_requisition()
        # Check rate manual should send to TE
        self.assertEqual(
            purchase_request.line_ids.mapped("requisition_lines.requisition_id")[
                :-1
            ].manual_currency,
            purchase_request.manual_currency,
        )
        self.assertEqual(
            purchase_request.line_ids.mapped("requisition_lines.requisition_id")[
                :-1
            ].type_currency,
            purchase_request.type_currency,
        )
        self.assertEqual(
            purchase_request.line_ids.mapped("requisition_lines.requisition_id")[
                :-1
            ].custom_rate,
            purchase_request.custom_rate,
        )
