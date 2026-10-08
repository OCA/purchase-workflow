##############################################################################
#
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
##############################################################################

from odoo import fields

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestPurchasePackageQty(AccountTestInvoicingCommon):
    def setUp(self):
        super().setUp()
        self.supplierinfo_model = self.env["product.supplierinfo"]
        self.purchase_order_line_model = self.env["purchase.order.line"]
        self.partner_1 = self.env.ref("base.res_partner_1")
        self.partner_2 = self.env.ref("base.res_partner_2")
        self.product = self.env.ref("product.product_product_4c")
        self.AccountMove = self.env["account.move"]
        self.journal_purchase = self.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )

        self.supplierinfo = self.supplierinfo_model.create(
            {
                "min_qty": 0.0,
                "partner_id": self.partner_2.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "package_qty": 10,
                "price_policy": "package",
                "base_price": 100,
                "indicative_package": True,
            }
        )

        self.purchase_order = self.env["purchase.order"].create(
            {"partner_id": self.partner_2.id}
        )
        self.po_line_1 = self.purchase_order_line_model.create(
            {
                "order_id": self.purchase_order.id,
                "product_id": self.product.id,
                "date_planned": fields.Datetime.now(),
                "name": "Test",
                "product_qty": 1,
                "product_uom": self.env.ref("uom.product_uom_categ_unit").id,
                "price_unit": 10.0,
            }
        )
        self.po_line_1.onchange_product_id()
        self.po_line_1.write({"product_qty_package": 2.0})
        self.po_line_1.onchange_product_qty_package()

    def test_001_purchase_order_partner_2_product_qty_package_2(self):
        self.assertEqual(self.po_line_1.product_qty, 20)

    def test_002_purchase_order_line_subtotal(self):
        self.assertEqual(self.po_line_1.price_subtotal, 200.0)

    def test_003_stock_move_package_qty(self):
        self.purchase_order.button_confirm()
        for move in self.po_line_1.move_ids:
            self.assertEqual(move.package_qty, self.po_line_1.package_qty)
            self.assertEqual(
                move.product_qty_package, self.po_line_1.product_qty_package
            )
            move.write({"quantity": move.product_uom_qty})
        self.purchase_order.picking_ids.button_validate()
        for move in self.po_line_1.move_ids:
            self.assertEqual(move.qty_done_package, move.product_qty_package)

    def test_004_check_invoice_line_qty(self):
        self.purchase_order.button_confirm()
        self.purchase_order.picking_ids.button_validate()
        account_move = self.AccountMove.create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner_2.id,
                "journal_id": self.journal_purchase.id,
                "currency_id": self.env.user.company_id.currency_id.id,
                "purchase_id": self.purchase_order.id,
            }
        )
        account_move._onchange_purchase_auto_complete()
        for line in account_move.invoice_line_ids:
            self.assertEqual(line.package_qty, line.purchase_line_id.package_qty)
            self.assertEqual(
                line.product_qty_package, line.purchase_line_id.product_qty_package
            )
            self.assertEqual(line.price_policy, line.purchase_line_id.price_policy)
