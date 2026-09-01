# Copyright 2017 Akretion (http://www.akretion.com)
# Copyright 2020 Camptocamp SA
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseException(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Useful models
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]
        cls.partner_id = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "type": "contact",
                "email": "test@test.com",
            }
        )
        cls.product_id_1 = cls.env["product.product"].create(
            {"name": "Test Product 1", "type": "consu"}
        )
        cls.product_id_2 = cls.env["product.product"].create(
            {"name": "Test Product 2", "type": "consu"}
        )
        cls.product_id_3 = cls.env["product.product"].create(
            {"name": "Test Product 3", "type": "consu"}
        )
        cls.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        cls.purchase_exception_confirm = cls.env["purchase.exception.confirm"]
        cls.exception_noemail = cls.env.ref("purchase_exception.po_excep_no_email")
        cls.exception_qtycheck = cls.env.ref("purchase_exception.pol_excep_qty_check")
        cls.po_vals = {
            "partner_id": cls.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product_id_1.name,
                        "product_id": cls.product_id_1.id,
                        "product_qty": 5.0,
                        "product_uom_id": cls.product_id_1.uom_id.id,
                        "price_unit": 500.0,
                        "date_planned": cls.date_planned,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": cls.product_id_2.name,
                        "product_id": cls.product_id_2.id,
                        "product_qty": 5.0,
                        "product_uom_id": cls.product_id_2.uom_id.id,
                        "price_unit": 250.0,
                        "date_planned": cls.date_planned,
                    },
                ),
            ],
        }
        cls.po_vals2 = {
            "partner_id": cls.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product_id_3.name,
                        "product_id": cls.product_id_3.id,
                        "product_qty": -1.0,
                        "product_uom_id": cls.product_id_3.uom_id.id,
                        "price_unit": 20.0,
                        "date_planned": cls.date_planned,
                    },
                ),
            ],
        }

    def test_purchase_order_exception(self):
        self.exception_noemail.active = True
        self.exception_qtycheck.active = True
        self.partner_id.email = False
        self.po = self.PurchaseOrder.create(self.po_vals.copy())

        # confirm quotation
        self.po.button_confirm()
        self.assertEqual(self.po.state, "draft")
        # test all draft po
        self.po2 = self.PurchaseOrder.create(self.po_vals.copy())

        self.PurchaseOrder.test_all_draft_orders()
        self.assertEqual(self.po2.state, "draft")
        # Set ignore_exception flag  (Done after ignore is selected at wizard)
        self.po.ignore_exception = True
        self.po.button_confirm()
        self.assertEqual(self.po.state, "purchase")

        # Add a order line to test after PO is confirmed
        field_onchange = self.PurchaseOrder._onchange_spec()
        self.assertEqual(field_onchange.get("order_line"), "1")
        self.po3New = self.PurchaseOrder.new(self.po_vals.copy())
        self.po3New.ignore_exception = True
        self.po3New.state = "purchase"
        self.po.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_id_3.name,
                            "product_id": self.product_id_3.id,
                            "product_qty": 2,
                            "product_uom_id": self.product_id_3.uom_id.id,
                            "price_unit": 30,
                            "date_planned": self.date_planned,
                        },
                    )
                ]
            }
        )

        # Set ignore exception True  (Done manually by user)
        self.po.ignore_exception = True
        self.po.button_cancel()
        self.po.button_draft()
        self.assertEqual(self.po.state, "draft")
        self.assertTrue(not self.po.ignore_exception)
        self.po.button_confirm()
        self.assertTrue(self.po.state, "to approve")

        # Simulation the opening of the wizard purchase_exception_confirm and
        # set ignore_exception to True
        po_except_confirm = self.purchase_exception_confirm.with_context(
            active_id=self.po.id,
            active_ids=[self.po.id],
            active_model=self.po._name,
        ).create({"ignore": True})
        po_except_confirm.action_confirm()

    def test_exception_qtycheck(self):
        # No allow ignoring exceptions if the "is_blocking" field is checked
        self.exception_qtycheck.active = True
        self.exception_qtycheck.is_blocking = True
        self.po = self.PurchaseOrder.create(self.po_vals2.copy())
        po_except_confirm = self.purchase_exception_confirm.with_context(
            **{
                "active_id": self.po.id,
                "active_ids": [self.po.id],
                "active_model": self.po._name,
            }
        ).create({"ignore": True})
        po_except_confirm.exception_ids = self.exception_qtycheck
        po_except_confirm.action_confirm()

    def test_purchase_get_lines(self):
        self.po4 = self.PurchaseOrder.create(self.po_vals2.copy())
        self.assertEqual(self.po4.ensure_one(), self.po4)
        self.po4._purchase_get_lines()
        self.assertEqual(len(self.po4.order_line), 1)
