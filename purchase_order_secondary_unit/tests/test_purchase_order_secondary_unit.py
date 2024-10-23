# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import Form, TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestPurchaseOrderSecondaryUnit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Active multiple units of measure security group for user
        cls.env.user.groups_id = [(4, cls.env.ref("uom.group_uom").id)]
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        # Create a product
        product_form = Form(cls.env["product.product"])
        product_form.name = "Test"
        product_form.uom_id = cls.product_uom_kg
        product_form.uom_po_id = cls.product_uom_kg
        cls.product = product_form.save()
        # Set a secondary unit on the template of the previously created product
        with Form(cls.product.product_tmpl_id) as template_form:
            with template_form.secondary_uom_ids.new() as secondary_uom_form:
                secondary_uom_form.name = "unit-700"
                secondary_uom_form.uom_id = cls.product_uom_unit
                secondary_uom_form.factor = 0.7
        cls.secondary_unit = cls.product.product_tmpl_id.secondary_uom_ids
        cls.product.purchase_secondary_uom_id = cls.secondary_unit.id
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        cls.purchase_order_obj = cls.env["purchase.order"]
        po_val = {
            "partner_id": cls.partner.id,
            "company_id": cls.env.company.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product.name,
                        "product_id": cls.product.id,
                        "product_qty": 1,
                        "product_uom": cls.product.uom_id.id,
                        "price_unit": 1000.00,
                        "date_planned": fields.Datetime.now(),
                    },
                )
            ],
        }
        po = cls.purchase_order_obj.new(po_val)
        po.onchange_partner_id()
        cls.order = cls.purchase_order_obj.create(po._convert_to_write(po._cache))

    def test_purchase_order_01(self):
        purchase_order = Form(self.order)
        with purchase_order.order_line.edit(0) as line:
            # Test _compute product_qty
            line.secondary_uom_id = self.secondary_unit
            line.secondary_uom_qty = 10.0
            self.assertEqual(line.product_qty, 7.0)
            # Test onchange product uom
            line.secondary_uom_qty = 3500.0
            line.product_uom = self.product_uom_gram
            self.assertEqual(line.secondary_uom_qty, 3.5)

    def test_purchase_order_02(self):
        purchase_order = Form(self.order)
        with purchase_order.order_line.new() as line_new:
            # Test default purchase order line secondary uom
            line_new.product_id = self.product
            self.assertEqual(line_new.secondary_uom_id, self.secondary_unit)
            self.assertEqual(line_new.secondary_uom_qty, 1.0)
            self.assertAlmostEqual(line_new.product_qty, 0.7, places=2)
