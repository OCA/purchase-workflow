# Copyright 2023 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestPRequisitionAnalyticRFQ(TransactionCase):
    def setUp(self):
        super().setUp()
        uom_unit = self.env.ref("uom.product_uom_unit")
        self.analytic_account_test = self.env["account.analytic.account"].create(
            {"name": "Test Account"}
        )
        self.product_order2 = self.env["product.product"].create(
            {
                "name": "Product2",
                "standard_price": 205.0,
                "list_price": 240.0,
                "type": "consu",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "purchase_method": "purchase",
                "default_code": "PROD_ORDER",
                "taxes_id": False,
            }
        )
        self.product_order3 = self.env["product.product"].create(
            {
                "name": "Product3",
                "standard_price": 295.0,
                "list_price": 240.0,
                "type": "consu",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "purchase_method": "purchase",
                "default_code": "PROD_ORDER",
                "taxes_id": False,
            }
        )
        self.partner = self.env["res.partner"].create({"name": "test partner"})
        self.requisition1 = self.env["purchase.requisition"].create(
            {
                "analytic_account_id": self.analytic_account_test.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_order3.id,
                            "product_qty": 10.0,
                            "product_uom_id": uom_unit.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_order2.id,
                            "product_qty": 10.0,
                            "product_uom_id": uom_unit.id,
                        },
                    ),
                ],
            }
        )

    def test_purchase_req_analyticrfq(self):
        po_form = Form(self.env["purchase.order"])
        po_form.partner_id = self.partner
        po_form.requisition_id = self.requisition1
        po = po_form.save()
        for line in po.order_line:
            self.assertEqual(
                line.account_analytic_id.id, self.requisition1.analytic_account_id.id
            )
