# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseRequisitionLineSupplierinfo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor"})
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "consu", "purchase_ok": True}
        )
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.vendor.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "price": 20.0,
                "delay": 55,
                "min_qty": 1000,
            }
        )
        cls.agreement = cls.env["purchase.requisition"].create(
            {
                "vendor_id": cls.vendor.id,
                "requisition_type": "blanket_order",
                "date_start": fields.Date.today(),
                "date_end": fields.Date.today() + timedelta(days=180),
                "line_ids": [
                    fields.Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_qty": 600,
                            "price_unit": 18.0,
                            "delay": 14,
                            "min_qty": 200,
                        }
                    )
                ],
            }
        )

    def test_confirm_writes_terms(self):
        self.agreement.action_confirm()
        seller = self.agreement.line_ids.supplier_info_ids
        self.assertEqual(len(seller), 1)
        self.assertEqual(seller.delay, 14)
        self.assertEqual(seller.min_qty, 200)
        self.assertEqual(seller.price, 18.0)

    def test_default_terms_match_standard(self):
        line = self.env["purchase.requisition.line"].new(
            {"product_id": self.product.id}
        )
        supplierinfo = self.env["product.supplierinfo"]
        self.assertEqual(line.delay, supplierinfo.default_get(["delay"])["delay"])
        self.assertEqual(line.min_qty, supplierinfo.default_get(["min_qty"])["min_qty"])

    def test_write_on_confirmed_agreement_updates_terms(self):
        self.agreement.action_confirm()
        self.agreement.line_ids.write({"delay": 21, "min_qty": 300})
        seller = self.agreement.line_ids.supplier_info_ids
        self.assertEqual(seller.delay, 21)
        self.assertEqual(seller.min_qty, 300)

    def test_line_added_to_confirmed_agreement(self):
        self.agreement.action_confirm()
        product = self.env["product.product"].create(
            {"name": "Product 2", "type": "consu", "purchase_ok": True}
        )
        line = self.env["purchase.requisition.line"].create(
            {
                "requisition_id": self.agreement.id,
                "product_id": product.id,
                "product_qty": 100,
                "price_unit": 5.0,
                "delay": 7,
                "min_qty": 50,
            }
        )
        self.assertEqual(line.supplier_info_ids.delay, 7)
        self.assertEqual(line.supplier_info_ids.min_qty, 50)

    def test_purchase_order_plans_on_agreement_lead_time(self):
        self.agreement.action_confirm()
        date_order = fields.Datetime.now()
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "requisition_id": self.agreement.id,
                "date_order": date_order,
                "order_line": [
                    fields.Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 200,
                            "uom_id": self.product.uom_id.id,
                        }
                    )
                ],
            }
        )
        line = order.order_line
        self.assertEqual(line.price_unit, 18.0)
        self.assertEqual(
            line.date_planned.date(), (date_order + timedelta(days=14)).date()
        )

    def test_new_quotation_plans_on_agreement_lead_time(self):
        self.agreement.action_confirm()
        with Form(
            self.env["purchase.order"].with_context(
                default_requisition_id=self.agreement.id
            )
        ) as order_form:
            order = order_form.save()
        line = order.order_line
        self.assertEqual(len(line), 1)
        self.assertEqual(
            line.date_planned.date(),
            (fields.Datetime.now() + timedelta(days=14)).date(),
        )

    def test_section_line(self):
        section = self.env["purchase.requisition.line"].create(
            {
                "requisition_id": self.agreement.id,
                "display_type": "line_section",
                "name": "Section",
                "sequence": 1,
            }
        )
        self.agreement.action_confirm()
        self.assertFalse(section.supplier_info_ids)
        with Form(
            self.env["purchase.order"].with_context(
                default_requisition_id=self.agreement.id
            )
        ) as order_form:
            order = order_form.save()
        self.assertEqual(
            order.order_line.mapped("display_type"), ["line_section", False]
        )

    def test_close_removes_supplierinfo(self):
        self.agreement.action_confirm()
        self.agreement.action_done()
        self.assertFalse(self.agreement.line_ids.supplier_info_ids)
