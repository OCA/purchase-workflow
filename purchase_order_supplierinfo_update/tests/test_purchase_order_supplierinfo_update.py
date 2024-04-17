# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form, TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPurchaseOrderSupplierinfoUpdate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.product = cls.env["product.product"].create(
            {"name": "Product Test", "type": "consu"}  # do not depend on stock module
        )
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier Test"})
        cls.supplierinfo = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.supplier.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "price": 100,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Product Test 2", "type": "consu"}
        )
        cls.supplierinfo_2 = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.supplier.id,
                "product_tmpl_id": cls.product_2.product_tmpl_id.id,
                "price": 10,
            }
        )

    def test_confirn_purchase_order(self):
        # Create a PO, confirm it and check the supplierinfo is updated
        po_form = Form(self.env["purchase.order"])
        po_form.partner_id = self.supplier
        with po_form.order_line.new() as po_line_form:
            po_line_form.product_id = self.product
            self.assertEqual(po_line_form.price_unit, 100)
            po_line_form.price_unit = 150
            po_line_form.taxes_id.clear()
        purchase_order = po_form.save()
        purchase_order.button_confirm()
        self.assertEqual(self.supplierinfo.price, 150)
        # Create another PO, confirm it and check the supplierinfo is updated
        po_form = Form(self.env["purchase.order"])
        po_form.partner_id = self.supplier
        with po_form.order_line.new() as po_line_form:
            po_line_form.product_id = self.product
            self.assertEqual(po_line_form.price_unit, 150)
            po_line_form.price_unit = 200
            po_line_form.taxes_id.clear()
        purchase_order = po_form.save()
        purchase_order.button_confirm()
        self.assertEqual(self.supplierinfo.price, 200)

    def test_change_price_in_confirmed_po(self):
        # Create first purchase
        po_form_1 = Form(self.env["purchase.order"])
        po_form_1.partner_id = self.supplier
        now = fields.Datetime.now()
        po_form_1.date_order = now - relativedelta(days=1)
        with po_form_1.order_line.new() as po_line_form:
            po_line_form.product_id = self.product
            po_line_form.taxes_id.clear()
        purchase_order_1 = po_form_1.save()
        purchase_order_1.button_confirm()
        # Create second purchase
        po_form_2 = Form(self.env["purchase.order"])
        po_form_2.partner_id = self.supplier
        with po_form_2.order_line.new() as po_line_form:
            po_line_form.product_id = self.product
            po_line_form.price_unit = 200
            po_line_form.taxes_id.clear()
        purchase_order_2 = po_form_2.save()
        purchase_order_2.button_confirm()
        # Change price in second purchase
        with Form(purchase_order_2) as po_form_2:
            with po_form_2.order_line.edit(0) as po_line_form:
                po_line_form.price_unit = 300
        self.assertEqual(self.supplierinfo.price, 300)
        # Change price in first purchase. This doesn't update supplierinfo
        # because it isn't the last purchase of this product by this supplier
        with Form(purchase_order_1) as po_form_1:
            with po_form_1.order_line.edit(0) as po_line_form:
                po_line_form.price_unit = 400
        self.assertEqual(self.supplierinfo.price, 300)

    def test_create_new_line_in_a_confirmed_po(self):
        # Create first purchase
        po_form_1 = Form(self.env["purchase.order"])
        po_form_1.partner_id = self.supplier
        with po_form_1.order_line.new() as po_line_form:
            po_line_form.product_id = self.product
            po_line_form.taxes_id.clear()
        purchase_order_1 = po_form_1.save()
        purchase_order_1.button_confirm()
        # Create second purchase
        po_form_2 = Form(self.env["purchase.order"])
        po_form_2.partner_id = self.supplier
        with po_form_2.order_line.new() as po_line_form:
            po_line_form.product_id = self.product
            po_line_form.price_unit = 200
            po_line_form.taxes_id.clear()
        purchase_order_2 = po_form_2.save()
        purchase_order_2.button_confirm()
        # Create a new line in the first purchase (that is already confirmed)
        # with another product.
        # We can not use a Form due to a modifier restriction on purchase order view
        # purchase/views/purchase_views.xml#L230
        purchase_order_1.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_2.id,
                            "product_uom": self.product_2.uom_po_id.id,
                            "price_unit": 20.00,
                        },
                    )
                ]
            }
        )
        self.assertEqual(self.supplierinfo_2.price, 20)
