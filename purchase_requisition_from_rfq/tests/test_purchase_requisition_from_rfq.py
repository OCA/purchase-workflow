# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPurchaseRequisitionFromRfq(TransactionCase):
    def setUp(self):
        super(TestPurchaseRequisitionFromRfq, self).setUp()
        # Useful models
        self.PurchaseRequisition = self.env["purchase.requisition"]
        self.PurchaseOrder = self.env["purchase.order"]
        # Partner
        self.partner_id_1 = self.env.ref("base.res_partner_1")
        self.partner_id_2 = self.env.ref("base.res_partner_2")
        self.partner_id_3 = self.env.ref("base.res_partner_3")
        # Product
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.product_id_2 = self.env.ref("product.product_product_11")
        # Date
        self.date_now = fields.Datetime.now()

    def test_create(self):
        PO_1 = self.PurchaseOrder.create(
            {
                "partner_id": self.partner_id_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_1.id,
                            "product_uom": self.product_id_1.uom_id.id,
                            "name": self.product_id_1.name,
                            "price_unit": self.product_id_1.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 10.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_2.id,
                            "product_uom": self.product_id_2.uom_id.id,
                            "name": self.product_id_2.name,
                            "price_unit": self.product_id_2.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 20.0,
                        },
                    ),
                ],
            }
        )
        PO_2 = self.PurchaseOrder.create(
            {
                "partner_id": self.partner_id_2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_1.id,
                            "product_uom": self.product_id_1.uom_id.id,
                            "name": self.product_id_1.name,
                            "price_unit": self.product_id_1.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 10.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_2.id,
                            "product_uom": self.product_id_2.uom_id.id,
                            "name": self.product_id_2.name,
                            "price_unit": self.product_id_2.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 20.0,
                        },
                    ),
                ],
            }
        )
        PO_3 = self.PurchaseOrder.create(
            {
                "partner_id": self.partner_id_2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_1.id,
                            "product_uom": self.product_id_1.uom_id.id,
                            "name": self.product_id_1.name,
                            "price_unit": self.product_id_1.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 30.0,
                        },
                    )
                ],
            }
        )
        # Error order difference
        with self.assertRaises(ValidationError):
            ctx = {"active_model": "purchase.order", "active_ids": [PO_1.id, PO_3.id]}
            self.PurchaseRequisition.with_context(ctx).create({})
        # Error order not draft
        PO_3.button_confirm()
        self.assertEqual(PO_3.state, "purchase")
        with self.assertRaises(ValidationError):
            ctx = {"active_model": "purchase.order", "active_ids": [PO_3.id]}
            self.PurchaseRequisition.with_context(ctx).create({})
        # Create agreement
        ctx = {"active_model": "purchase.order", "active_ids": [PO_1.id, PO_2.id]}
        self.PurchaseRequisition.with_context(ctx).create({})
        # Error agreement created
        with self.assertRaises(ValidationError):
            ctx = {"active_model": "purchase.order", "active_ids": [PO_1.id]}
            self.PurchaseRequisition.with_context(ctx).create({})

    def test_auto_cancel(self):
        PO_1 = self.PurchaseOrder.create(
            {
                "partner_id": self.partner_id_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_1.id,
                            "product_uom": self.product_id_1.uom_id.id,
                            "name": self.product_id_1.name,
                            "price_unit": self.product_id_1.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 10.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_2.id,
                            "product_uom": self.product_id_2.uom_id.id,
                            "name": self.product_id_2.name,
                            "price_unit": self.product_id_2.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 20.0,
                        },
                    ),
                ],
            }
        )
        PO_2 = self.PurchaseOrder.create(
            {
                "partner_id": self.partner_id_2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_1.id,
                            "product_uom": self.product_id_1.uom_id.id,
                            "name": self.product_id_1.name,
                            "price_unit": self.product_id_1.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 10.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_2.id,
                            "product_uom": self.product_id_2.uom_id.id,
                            "name": self.product_id_2.name,
                            "price_unit": self.product_id_2.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 20.0,
                        },
                    ),
                ],
            }
        )
        # Create agreement
        ctx = {
            "active_model": "purchase.order",
            "active_ids": [PO_1.id, PO_2.id],
            "default_from_rfq": True,
        }
        self.PurchaseRequisition.with_context(ctx).create({})

        # Before confirm order
        self.assertEqual(PO_1.state, "draft")
        self.assertEqual(PO_2.state, "draft")
        # After confirm order
        PO_1.button_confirm()
        self.assertEqual(PO_1.state, "purchase")
        self.assertEqual(PO_2.state, "cancel")
