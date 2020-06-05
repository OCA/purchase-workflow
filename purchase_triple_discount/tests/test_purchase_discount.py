# Copyright 2017-19 Tecnativa - David Vidal
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        cls.supplierinfo_obj = cls.env["product.supplierinfo"]
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Mrs. Odoo"})
        cls.product1 = cls.env["product.product"].create(
            {"name": "Test Product 1", "purchase_method": "purchase"}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "Test Product 2", "purchase_method": "purchase"}
        )
        cls.supplierinfo = cls.supplierinfo_obj.create(
            {
                "min_qty": 0.0,
                "name": cls.partner2.id,
                "product_tmpl_id": cls.product1.product_tmpl_id.id,
                "discount": 10,
                "discount2": 20,
                "discount3": 30,
            }
        )
        cls.supplierinfo2 = cls.supplierinfo_obj.create(
            {
                "min_qty": 10.0,
                "name": cls.partner2.id,
                "product_tmpl_id": cls.product1.product_tmpl_id.id,
                "discount3": 50,
            }
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "amount": 15.0,
            }
        )
        cls.order = cls.env["purchase.order"].create({"partner_id": cls.partner.id})
        cls.order2 = cls.env["purchase.order"].create({"partner_id": cls.partner2.id})
        po_line = cls.env["purchase.order.line"]
        cls.po_line1 = po_line.create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product1.id,
                "date_planned": "2018-01-19 00:00:00",
                "name": "Line 1",
                "product_qty": 1.0,
                "product_uom": cls.product1.uom_id.id,
                "taxes_id": [(6, 0, [cls.tax.id])],
                "price_unit": 600.0,
            }
        )
        cls.po_line2 = po_line.create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product2.id,
                "date_planned": "2018-01-19 00:00:00",
                "name": "Line 2",
                "product_qty": 10.0,
                "product_uom": cls.product2.uom_id.id,
                "taxes_id": [(6, 0, [cls.tax.id])],
                "price_unit": 60.0,
            }
        )
        cls.po_line3 = po_line.create(
            {
                "order_id": cls.order2.id,
                "product_id": cls.product1.id,
                "date_planned": "2020-01-01 00:00:00",
                "name": "Line 1",
                "product_qty": 1.0,
                "product_uom": cls.product1.uom_id.id,
                "taxes_id": [(6, 0, [cls.tax.id])],
                "price_unit": 600.0,
            }
        )

    def test_01_purchase_order_classic_discount(self):
        """ Tests with single discount """
        self.po_line1.discount = 50.0
        self.po_line2.discount = 75.0
        self.assertEqual(self.po_line1.price_subtotal, 300.0)
        self.assertEqual(self.po_line2.price_subtotal, 150.0)
        self.assertEqual(self.order.amount_untaxed, 450.0)
        self.assertEqual(self.order.amount_tax, 67.5)
        # Mix taxed and untaxed:
        self.po_line1.taxes_id = False
        self.assertEqual(self.order.amount_tax, 22.5)

    def test_02_purchase_order_simple_triple_discount(self):
        """ Tests on a single line """
        self.po_line2.unlink()
        # Divide by two on every discount:
        self.po_line1.discount = 50.0
        self.po_line1.discount2 = 50.0
        self.po_line1.discount3 = 50.0
        self.assertEqual(self.po_line1.price_subtotal, 75.0)
        self.assertEqual(self.order.amount_untaxed, 75.0)
        self.assertEqual(self.order.amount_tax, 11.25)
        # Unset first discount:
        self.po_line1.discount = 0.0
        self.assertEqual(self.po_line1.price_subtotal, 150.0)
        self.assertEqual(self.order.amount_untaxed, 150.0)
        self.assertEqual(self.order.amount_tax, 22.5)
        # Set a charge instead:
        self.po_line1.discount2 = -50.0
        self.assertEqual(self.po_line1.price_subtotal, 450.0)
        self.assertEqual(self.order.amount_untaxed, 450.0)
        self.assertEqual(self.order.amount_tax, 67.5)

    def test_03_purchase_order_complex_triple_discount(self):
        """ Tests on multiple lines """
        self.po_line1.discount = 50.0
        self.po_line1.discount2 = 50.0
        self.po_line1.discount3 = 50.0
        self.assertEqual(self.po_line1.price_subtotal, 75.0)
        self.assertEqual(self.order.amount_untaxed, 675.0)
        self.assertEqual(self.order.amount_tax, 101.25)
        self.po_line2.discount3 = 50.0
        self.assertEqual(self.po_line2.price_subtotal, 300.0)
        self.assertEqual(self.order.amount_untaxed, 375.0)
        self.assertEqual(self.order.amount_tax, 56.25)

    def test_04_purchase_order_triple_discount_invoicing(self):
        """ When a confirmed order is invoiced, the resultant invoice
            should inherit the discounts """
        self.po_line1.discount = 50.0
        self.po_line1.discount2 = 50.0
        self.po_line1.discount3 = 50.0
        self.po_line2.discount3 = 50.0
        self.order.button_confirm()
        self.invoice = self.env["account.move"].new(
            {
                "partner_id": self.partner.id,
                "purchase_id": self.order.id,
                "type": "in_invoice",
            }
        )
        self.invoice._onchange_purchase_auto_complete()
        self.assertEqual(
            self.po_line1.discount, self.invoice.invoice_line_ids[0].discount1
        )
        self.assertEqual(
            self.po_line1.discount2, self.invoice.invoice_line_ids[0].discount2
        )
        self.assertEqual(
            self.po_line1.discount3, self.invoice.invoice_line_ids[0].discount3
        )
        self.assertEqual(
            self.po_line2.discount3, self.invoice.invoice_line_ids[1].discount3
        )
        self.assertEqual(self.order.amount_total, self.invoice.amount_total)

    def test_05_purchase_order_default_discounts(self):
        self.po_line3._onchange_quantity()
        self.assertEquals(self.po_line3.discount, 10)
        self.assertEquals(self.po_line3.discount2, 20)
        self.assertEquals(self.po_line3.discount3, 30)
        self.po_line3.product_qty = 10
        self.po_line3._onchange_quantity()
        self.assertFalse(self.po_line3.discount)
        self.assertFalse(self.po_line3.discount2)
        self.assertEquals(self.po_line3.discount3, 50)

    def test_06_default_supplier_discounts(self):
        self.partner2.default_supplierinfo_discount = 11
        self.partner2.default_supplierinfo_discount2 = 22
        self.partner2.default_supplierinfo_discount3 = 33
        supplierinfo = self.supplierinfo_obj.new(
            {
                "min_qty": 0.0,
                "name": self.partner2.id,
                "product_tmpl_id": self.product1.product_tmpl_id.id,
                "discount": 10,
            }
        )
        supplierinfo.onchange_name()
        self.assertEquals(supplierinfo.discount, 11)
        self.assertEquals(supplierinfo.discount2, 22)
        self.assertEquals(supplierinfo.discount3, 33)

    def test_07_supplierinfo_from_purchaseorder(self):
        self.order2.order_line.create(
            {
                "order_id": self.order2.id,
                "product_id": self.product2.id,
                "date_planned": "2020-01-01 00:00:00",
                "name": "Line 2",
                "product_qty": 1.0,
                "product_uom": self.product2.uom_id.id,
                "taxes_id": [(6, 0, [self.tax.id])],
                "price_unit": 999.0,
                "discount": 11.11,
                "discount2": 22.22,
                "discount3": 33.33,
            }
        )
        self.order2.button_confirm()
        seller = self.supplierinfo_obj.search(
            [
                ("name", "=", self.partner2.id),
                ("product_tmpl_id", "=", self.product2.product_tmpl_id.id),
            ]
        )
        self.assertTrue(seller)
        self.assertEqual(seller.discount, 11.11)
        self.assertEqual(seller.discount2, 22.22)
        self.assertEqual(seller.discount3, 33.33)

    def test_08_purchase_report(self):
        self.po_line2.write({"discount2": 50, "discount3": 20})
        self.order.currency_id.rate_ids.unlink()  # for avoiding rate convers.
        rec = self.env["purchase.report"].search(
            [("product_id", "=", self.product2.id)]
        )
        self.assertEqual(rec.discount2, 50)
        self.assertEqual(rec.discount3, 20)
        self.assertEqual(rec.untaxed_total, 240)
        self.assertEqual(rec.price_total, 276)
