##############################################################################
#
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
##############################################################################

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPurchasePackageQty(AccountTestInvoicingCommon):
    def setUp(self):
        super().setUp()
        self.env.user.groups_id |= self.env.ref("product.group_stock_packaging")
        self.supplierinfo_model = self.env["product.supplierinfo"]
        self.purchase_order_line_model = self.env["purchase.order.line"]
        self.partner_1 = self.env.ref("base.res_partner_1")
        self.partner_2 = self.env.ref("base.res_partner_2")
        tax_group = self.env["account.tax.group"].create(
            [
                {
                    "name": "Test Tax Group 25",
                    "company_id": self.env.company.id,
                }
            ]
        )
        tax_25 = self.env["account.tax"].create(
            {
                "name": "Test Tax 25%",
                "type_tax_use": "purchase",
                "amount_type": "percent",
                "amount": 25,
                "tax_group_id": tax_group.id,
                "company_id": self.env.company.id,
            }
        )
        self.product = self.env.ref("product.product_product_4c")
        self.product.supplier_taxes_id = tax_25
        self.product.purchase_method = "purchase"
        self.AccountMove = self.env["account.move"]
        self.journal_purchase = self.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )

        self.packaging_single = self.env["product.packaging"].create(
            {
                "name": "I'm a packaging",
                "product_id": self.product.id,
                "qty": 5.0,
            }
        )
        self.packaging_dozen = self.env["product.packaging"].create(
            {
                "name": "I'm also a packaging",
                "product_id": self.product.id,
                "qty": 12.0,
            }
        )

        self.supplierinfo = self.supplierinfo_model.create(
            [
                {
                    "min_qty": 0.0,
                    "partner_id": self.partner_2.id,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "price_policy": "uom",
                    "indicative_package": False,
                    # "product_packaging_id": self.packaging_single.id,
                    "package_qty": 5,
                },
                {
                    "min_qty": 12,
                    "partner_id": self.partner_2.id,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "price_policy": "package",
                    "indicative_package": True,
                    # "product_packaging_id": self.packaging_dozen.id,
                    "package_qty": 12,
                },
            ]
        )
        self.supplierinfo[0].base_price = 20
        self.supplierinfo[1].base_price = 17 * 12

        self.purchase_order = self.env["purchase.order"].create(
            {"partner_id": self.partner_2.id}
        )
        self.po_line_1 = self.purchase_order_line_model.create(
            {
                "order_id": self.purchase_order.id,
                "product_id": self.product.id,
                "date_planned": fields.Datetime.now(),
                "name": "Test line 1",
                "product_uom": self.env.ref("uom.product_uom_categ_unit").id,
                "price_policy": "uom",
                # "price_unit": 10.0,
                "package_qty": 5,
                "product_qty": 5,
                "product_packaging_qty": 1,
                # "indicative_package": True,
            }
        )
        # Same product but different packaging
        self.po_line_2 = self.purchase_order_line_model.create(
            {
                "order_id": self.purchase_order.id,
                "product_id": self.product.id,
                "date_planned": fields.Datetime.now(),
                "name": "Test line 2",
                "product_uom": self.env.ref("uom.product_uom_categ_unit").id,
                "price_policy": "uom",
                # "price_unit": 10.0,
                "package_qty": 12,
                "product_qty": 12,
                "product_packaging_qty": 1,
            }
        )

    def test_000_product_supplier_info_package(self):
        # Test creation of product supplierinfo with packaging
        product_form = Form(self.product)
        with product_form.variant_seller_ids.new() as psi:
            psi.partner_id = self.partner_1
            psi.package_qty = 12
            # psi.product_packaging_id = self.packaging_dozen
            # self.assertEqual(psi.package_qty, 12)
            self.assertEqual(psi.base_price, 0)
            self.assertEqual(psi.price, 0)
            psi.base_price = 19
            self.assertEqual(psi.price, 19)
            psi.price_policy = "package"
            self.assertEqual(psi.price, 19 / 12)
            self.assertEqual(psi.base_price, 19)
            psi.base_price = 18 * 12
            self.assertEqual(psi.price, 18)

    def test_001_purchasing_flow(self):
        # Test flow from purchase order to receipt and vendor bill
        # First, test the computed values on the PO lines
        self.assertEqual(self.po_line_1.package_qty, 5)
        self.assertEqual(self.po_line_2.package_qty, 12)
        self.assertEqual(self.po_line_1.product_packaging_qty, 1)
        self.assertEqual(self.po_line_2.product_packaging_qty, 1)
        self.assertEqual(self.po_line_1.product_qty, 5)
        self.assertEqual(self.po_line_2.product_qty, 12)
        # price_policy is `uom` by default for 2 lines
        self.assertEqual(self.po_line_1.price_policy, "uom")
        self.assertEqual(self.po_line_2.price_policy, "uom")
        self.assertFalse(self.po_line_1.indicative_package)
        self.assertFalse(self.po_line_2.indicative_package)

        # Second, onchange the product to trigger the computation
        po_form = Form(self.purchase_order)
        with po_form.order_line.edit(1) as line_form:
            line_form.price_policy = "uom"  # to trigger the onchange
            self.assertEqual(line_form.price_unit, 17)
            line_form.product_id = self.product
            line_form.product_packaging_qty = 2
            # Qty is 24 now, it loads the psi of packaging_dozen because of min qty
            self.assertEqual(line_form.price_policy, "package")
            self.assertEqual(line_form.product_qty, 24)
            # Price unit change from 17 to 17*12: per unit to per package
            self.assertEqual(line_form.price_unit, 17 * 12)
            self.assertTrue(line_form.indicative_package)

        with po_form.order_line.edit(0) as line_form:
            line_form.price_policy = "package"
            # Test subtotal updated as well
            self.assertEqual(line_form.price_unit, 20 * 5)
            line_form.price_policy = "uom"
            self.assertEqual(line_form.price_unit, 20)

        # po_form.button_confirm()
        # Module purchase_order_type make order_type required from the form
        # So, po_form.save() failed because of
        # `AssertionError: order_type is a required field`
        values = po_form._get_values("onchange")
        self.purchase_order.update(values)
        self.purchase_order.order_line[1].price_policy = "uom"
        # po_form.save()

        amount_line1 = 5 * 20  # product qty*price (price_policy=uom)
        amount_line2 = 2 * (17 * 12)  # package qty*price (price_policy=package)
        untax_amount = amount_line1 + amount_line2
        self.assertEqual(self.purchase_order.order_line[0].price_subtotal, amount_line1)
        self.assertEqual(self.purchase_order.order_line[1].price_subtotal, amount_line2)
        self.assertEqual(self.purchase_order.amount_untaxed, untax_amount)
        self.assertEqual(self.purchase_order.amount_tax, untax_amount * 0.25)  # tax 25%
        self.assertEqual(self.purchase_order.amount_total, untax_amount * 1.25)

        # Test related picking
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids
        # Test values copied from PO line
        for stock_move, idx in zip(picking.move_ids, [0, 1], strict=False):
            po_line = self.purchase_order.order_line[idx]
            self.assertEqual(
                stock_move.product_qty_package, po_line.product_qty_package
            )

        # Test invoice values
        self.purchase_order.action_create_invoice()
        invoice = self.purchase_order.invoice_ids[0]
        for invoice_line, idx in zip(invoice.invoice_line_ids, [0, 1], strict=False):
            po_line = self.purchase_order.order_line[idx]
            self.assertEqual(
                invoice_line.product_qty_package, po_line.product_packaging_qty
            )
            self.assertEqual(invoice_line.price_policy, po_line.price_policy)
            self.assertEqual(invoice_line.quantity, po_line.product_uom_qty)
            self.assertEqual(
                invoice_line.product_qty_package, po_line.product_packaging_qty
            )
            self.assertEqual(invoice_line.price_subtotal, po_line.price_subtotal)
        # Check total values
        self.assertEqual(self.purchase_order.amount_untaxed, invoice.amount_untaxed)
        self.assertEqual(self.purchase_order.amount_tax, invoice.amount_tax)
        self.assertEqual(self.purchase_order.amount_total, invoice.amount_total)

    def test_002_manual_receipt(self):
        # Create the receipt manually
        picking_form = Form(
            self.env["stock.picking"].with_context(
                restricted_picking_type_code="incoming"
            )
        )
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            move.package_qty = 12
            move.product_qty_package = 3
            self.assertEqual(move.product_uom_qty, 3 * 12)
        picking = picking_form.save()
        picking.action_confirm()
        self.assertEqual(picking.move_ids_without_package[0].product_qty_package, 3)

    def test_003_manual_invoice(self):
        # Create the vendor bill manually
        bill_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        with bill_form.invoice_line_ids.new() as line:
            line.product_id = self.product
            line.package_qty = 12
            line.price_unit = 17
            line.product_qty_package = 3
            self.assertEqual(line.price_policy, "uom")  # by default value
            self.assertEqual(line.quantity, 3 * 12)
            self.assertEqual(line.price_subtotal, 17 * line.quantity)

            # Change the policy
            line.price_policy = "package"
            self.assertEqual(line.price_subtotal, 17 * 3)

    def test_004_check_indicative_package(self):
        line_1 = self.purchase_order.order_line[0]
        # line_2 = self.purchase_order.order_line[1]
        self.assertFalse(line_1.indicative_package)
        with self.assertRaises(ValidationError):
            line_1.product_qty += 1
        line_1.indicative_package = True
        # Ok to update the qty
        line_1.product_qty += 1
        self.assertEqual(line_1.product_qty, 6)
