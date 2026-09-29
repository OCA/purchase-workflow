# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Datetime
from odoo.tests.common import TransactionCase


class TestPurchaseOpenQty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order_model = cls.env["purchase.order"]
        purchase_order_line_model = cls.env["purchase.order.line"]
        partner_model = cls.env["res.partner"]
        prod_model = cls.env["product.product"]
        analytic_account_model = cls.env["account.analytic.account"]

        # partners
        pa_dict = {"name": "Partner 1"}
        cls.partner = partner_model.sudo().create(pa_dict)
        pa_dict2 = {"name": "Partner 2"}
        cls.partner2 = partner_model.sudo().create(pa_dict2)

        # account
        ac_dict = {
            "name": "analytic account 1",
            "plan_id": cls.env.ref("analytic.analytic_plan_projects").id,
        }
        cls.analytic_account_1 = analytic_account_model.sudo().create(ac_dict)

        # Purchase Order Num 1
        po_dict = {"partner_id": cls.partner.id}
        cls.purchase_order_1 = cls.purchase_order_model.create(po_dict)
        uom_id = prod_model.uom_id.search([("name", "=", "Units")], limit=1).id
        pr_dict = {
            "name": "Product Test",
            "uom_id": uom_id,
            "purchase_method": "purchase",
        }
        cls.product = prod_model.sudo().create(pr_dict)
        pl_dict1 = {
            "date_planned": Datetime.now(),
            "name": "PO01",
            "order_id": cls.purchase_order_1.id,
            "product_id": cls.product.id,
            "product_uom": uom_id,
            "price_unit": 1.0,
            "product_qty": 5.0,
            "analytic_distribution": {cls.analytic_account_1.id: 100},
        }
        cls.purchase_order_line_1 = purchase_order_line_model.sudo().create(pl_dict1)
        cls.purchase_order_1.button_confirm()

        # Purchase Order Num 2
        po_dict2 = {"partner_id": cls.partner2.id}
        cls.purchase_order_2 = cls.purchase_order_model.create(po_dict2)
        pr_dict2 = {
            "name": "Product Test 2",
            "uom_id": uom_id,
            "purchase_method": "receive",
        }
        cls.product2 = prod_model.sudo().create(pr_dict2)
        pl_dict2 = {
            "date_planned": Datetime.now(),
            "name": "PO02",
            "order_id": cls.purchase_order_2.id,
            "product_id": cls.product2.id,
            "product_uom": uom_id,
            "price_unit": 1.0,
            "product_qty": 5.0,
            "analytic_distribution": {cls.analytic_account_1.id: 100},
        }
        cls.purchase_order_line_2 = purchase_order_line_model.sudo().create(pl_dict2)
        cls.purchase_order_2.button_confirm()

        # Purchase Order Num 3 (service)
        po_dict3 = {"partner_id": cls.partner2.id}
        cls.purchase_order_3 = cls.purchase_order_model.create(po_dict3)
        pr_dict3 = {
            "name": "Product Test 3",
            "uom_id": uom_id,
            "purchase_method": "receive",
            "type": "service",
        }
        cls.product3 = prod_model.sudo().create(pr_dict3)
        pl_dict3 = {
            "date_planned": Datetime.now(),
            "name": "PO03",
            "order_id": cls.purchase_order_3.id,
            "product_id": cls.product3.id,
            "product_uom": uom_id,
            "price_unit": 10.0,
            "product_qty": 5.0,
        }
        cls.purchase_order_line_3 = purchase_order_line_model.sudo().create(pl_dict3)
        cls.purchase_order_3.button_confirm()

    def test_compute_qty_to_invoice_and_receive(self):
        self.assertEqual(
            self.purchase_order_line_1.qty_to_invoice,
            5.0,
            "Expected 5 as qty_to_invoice in the PO line",
        )
        self.assertEqual(
            self.purchase_order_line_1.qty_to_receive,
            5.0,
            "Expected 5 as qty_to_receive in the PO line",
        )
        self.assertEqual(
            self.purchase_order_1.qty_to_invoice,
            5.0,
            "Expected 5 as qty_to_invoice in the PO",
        )
        self.assertEqual(
            self.purchase_order_1.qty_to_receive,
            5.0,
            "Expected 5 as qty_to_receive in the PO",
        )

        self.assertEqual(
            self.purchase_order_line_2.qty_to_invoice,
            0.0,
            "Expected 0 as qty_to_invoice in the PO line",
        )
        self.assertEqual(
            self.purchase_order_line_2.qty_to_receive,
            5.0,
            "Expected 5 as qty_to_receive in the PO line",
        )
        self.assertEqual(
            self.purchase_order_2.qty_to_invoice,
            0.0,
            "Expected 0 as qty_to_invoice in the PO",
        )
        self.assertEqual(
            self.purchase_order_2.qty_to_receive,
            5.0,
            "Expected 5 as qty_to_receive in the PO",
        )

        # Now we receive the products
        for picking in self.purchase_order_2.picking_ids:
            picking.action_confirm()
            picking.move_ids.write({"quantity": 5.0})
            picking.button_validate()

        # The value is computed when you run it as at user but not in the test
        self.purchase_order_2._compute_qty_to_invoice()
        self.purchase_order_2._compute_qty_to_receive()

        self.assertEqual(
            self.purchase_order_line_2.qty_to_invoice,
            5.0,
            "Expected 5 as qty_to_invoice in the PO line",
        )
        self.assertEqual(
            self.purchase_order_line_2.qty_to_receive,
            0.0,
            "Expected 0 as qty_to_receive in the PO line",
        )
        self.assertEqual(
            self.purchase_order_2.qty_to_invoice,
            5.0,
            "Expected 5 as qty_to_invoice in the PO",
        )
        self.assertEqual(
            self.purchase_order_2.qty_to_receive,
            0.0,
            "Expected 0 as qty_to_receive in the PO",
        )

    def test_search_qty_to_invoice_and_receive(self):
        found = self.purchase_order_model.search(
            [
                "|",
                ("pending_qty_to_invoice", "=", True),
                ("pending_qty_to_receive", "=", True),
            ]
        )
        self.assertTrue(
            self.purchase_order_1.id in found.ids,
            f"Expected PO {self.purchase_order_1.id} in POs {found.ids}",
        )
        found = self.purchase_order_model.search(
            [
                "|",
                ("pending_qty_to_invoice", "=", False),
                ("pending_qty_to_receive", "=", False),
            ]
        )
        self.assertFalse(
            self.purchase_order_2.id not in found.ids,
            f"Expected PO {self.purchase_order_2.id} not to be in POs {found.ids}",
        )

    def test_03_po_line_with_services(self):
        self.assertEqual(
            self.purchase_order_line_3.qty_to_receive,
            5.0,
        )
        self.assertEqual(
            self.purchase_order_line_3.qty_received,
            0.0,
        )
        self.purchase_order_line_3.qty_received = 3.0
        self.assertEqual(
            self.purchase_order_line_3.qty_to_receive,
            2.0,
        )
        self.assertEqual(
            self.purchase_order_line_3.qty_received,
            3.0,
        )
        self.assertEqual(
            self.purchase_order_line_3.qty_to_invoice,
            3.0,
        )
