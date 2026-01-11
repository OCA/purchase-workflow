# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged

from .common import TestPurchaseSecondaryUnitCommon


@tagged("-at_install", "post_install")
class TestProductSupplierinfoSecondaryUnit(TestPurchaseSecondaryUnitCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplierinfo = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.partner.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "price": 100.0,
            }
        )

    def test_supplierinfo_secondary_uom_price_compute(self):
        self.supplierinfo.secondary_uom_id = self.secondary_unit
        # price = 100, factor = 0.7, secondary_uom_price = 70
        self.assertEqual(self.supplierinfo.secondary_uom_price, 70.0)

    def test_supplierinfo_secondary_uom_price_inverse(self):
        self.supplierinfo.secondary_uom_id = self.secondary_unit
        self.supplierinfo.secondary_uom_price = 140.0
        # secondary_uom_price = 140, factor = 0.7, price = 200
        self.assertEqual(self.supplierinfo.price, 200.0)

    def test_supplierinfo_no_secondary_unit(self):
        self.supplierinfo.secondary_uom_id = False
        self.assertEqual(self.supplierinfo.secondary_uom_price, 0.0)

    def test_supplierinfo_onchange_product_tmpl_id_secondary_uom(self):
        self.product.product_tmpl_id.purchase_secondary_uom_id = self.secondary_unit
        supplierinfo_form = Form(
            self.env["product.supplierinfo"].with_context(
                default_product_tmpl_id=self.product.product_tmpl_id.id
            )
        )
        supplierinfo_form.partner_id = self.partner
        self.assertEqual(supplierinfo_form.secondary_uom_id, self.secondary_unit)

    def test_supplierinfo_onchange_product_id_secondary_uom(self):
        self.product.purchase_secondary_uom_id = self.secondary_unit
        supplierinfo_form = Form(
            self.env["product.supplierinfo"].with_context(
                default_product_id=self.product.id,
                default_product_tmpl_id=self.product.product_tmpl_id.id,
            )
        )
        supplierinfo_form.partner_id = self.partner
        self.assertEqual(supplierinfo_form.secondary_uom_id, self.secondary_unit)

    def test_supplierinfo_onchange_product_variant_takes_precedence(self):
        secondary_unit_2 = self.env["product.secondary.unit"].create(
            {
                "name": "Pallet",
                "uom_id": self.product_uom_unit.id,
                "factor": 48.0,
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )
        self.product.product_tmpl_id.purchase_secondary_uom_id = self.secondary_unit
        self.product.purchase_secondary_uom_id = secondary_unit_2
        supplierinfo_form = Form(
            self.env["product.supplierinfo"].with_context(
                default_product_id=self.product.id,
                default_product_tmpl_id=self.product.product_tmpl_id.id,
            )
        )
        supplierinfo_form.partner_id = self.partner
        self.assertEqual(supplierinfo_form.secondary_uom_id, secondary_unit_2)
