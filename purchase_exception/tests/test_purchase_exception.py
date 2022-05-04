# Copyright 2017 Akretion (http://www.akretion.com)
# Copyright 2020 Camptocamp SA
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestPurchaseException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Useful models
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]
        cls.partner_id = cls.env.ref("base.res_partner_1")
        cls.product_id_1 = cls.env.ref("product.product_product_6")
        cls.product_id_2 = cls.env.ref("product.product_product_7")
        cls.product_id_3 = cls.env.ref("product.product_product_7")
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
                        "product_uom": cls.product_id_1.uom_po_id.id,
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
                        "product_uom": cls.product_id_2.uom_po_id.id,
                        "price_unit": 250.0,
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
        # set ignore_exception = False  (Done by onchange of order_line)
        field_onchange = self.PurchaseOrder._onchange_spec()
        self.assertEqual(field_onchange.get("order_line"), "1")
        self.env.cache.invalidate()
        self.po3New = self.PurchaseOrder.new(self.po_vals.copy())
        self.po3New.ignore_exception = True
        self.po3New.state = "purchase"
        self.po3New.onchange_ignore_exception()
        self.assertFalse(self.po3New.ignore_exception)
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
                            "product_uom": self.product_id_3.uom_id.id,
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
        self.assertTrue(self.po.ignore_exception)
