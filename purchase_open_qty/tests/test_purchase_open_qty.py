# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Datetime
from odoo.tests.common import TransactionCase


class TestPurchaseOpenQty(TransactionCase):
    def setUp(self):
        super(TestPurchaseOpenQty, self).setUp()
        self.purchase_order_model = self.env["purchase.order"]
        purchase_order_line_model = self.env["purchase.order.line"]
        partner_model = self.env["res.partner"]
        prod_model = self.env["product.product"]
        analytic_account_model = self.env["account.analytic.account"]

        # partners
        pa_dict = {"name": "Partner 1"}
        self.partner = partner_model.sudo().create(pa_dict)
        pa_dict2 = {"name": "Partner 2"}
        self.partner2 = partner_model.sudo().create(pa_dict2)

        # account
        ac_dict = {"name": "analytic account 1"}
        self.analytic_account_1 = analytic_account_model.sudo().create(ac_dict)

        # Purchase Order Num 1
        po_dict = {"partner_id": self.partner.id}
        self.purchase_order_1 = self.purchase_order_model.create(po_dict)
        uom_id = prod_model.uom_id.search([("name", "=", "Units")], limit=1).id
        pr_dict = {
            "name": "Product Test",
            "uom_id": uom_id,
            "purchase_method": "purchase",
        }
        self.product = prod_model.sudo().create(pr_dict)
        pl_dict1 = {
            "date_planned": Datetime.now(),
            "name": "PO01",
            "order_id": self.purchase_order_1.id,
            "product_id": self.product.id,
            "product_uom": uom_id,
            "price_unit": 1.0,
            "product_qty": 5.0,
            "account_analytic_id": self.analytic_account_1.id,
        }
        self.purchase_order_line_1 = purchase_order_line_model.sudo().create(pl_dict1)
        self.purchase_order_1.button_confirm()

        # Purchase Order Num 2
        po_dict2 = {"partner_id": self.partner2.id}
        self.purchase_order_2 = self.purchase_order_model.create(po_dict2)
        pr_dict2 = {
            "name": "Product Test 2",
            "uom_id": uom_id,
            "purchase_method": "receive",
        }
        self.product2 = prod_model.sudo().create(pr_dict2)
        pl_dict2 = {
            "date_planned": Datetime.now(),
            "name": "PO02",
            "order_id": self.purchase_order_2.id,
            "product_id": self.product2.id,
            "product_uom": uom_id,
            "price_unit": 1.0,
            "product_qty": 5.0,
            "account_analytic_id": self.analytic_account_1.id,
        }
        self.purchase_order_line_2 = purchase_order_line_model.sudo().create(pl_dict2)
        self.purchase_order_2.button_confirm()

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
            picking.move_lines.write({"quantity_done": 5.0})
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
            "Expected PO {} in POs {}".format(self.purchase_order_1.id, found.ids),
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
            "Expected PO %s not to be in POs %s"
            % (self.purchase_order_2.id, found.ids),
        )
