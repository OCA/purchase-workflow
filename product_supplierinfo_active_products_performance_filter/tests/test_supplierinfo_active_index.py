# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSupplierinfoActiveIndex(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.template = cls.env["product.template"].create({"name": "Test Product"})
        cls.variant = cls.template.product_variant_ids[0]
        cls.si_tmpl = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.partner.id,
                "product_tmpl_id": cls.template.id,
                "price": 10.0,
            }
        )
        cls.si_variant = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.partner.id,
                "product_tmpl_id": cls.template.id,
                "product_id": cls.variant.id,
                "price": 12.0,
            }
        )

    def test_new_record_defaults_to_active(self):
        """Newly created supplierinfo records should default to active."""
        self.assertTrue(self.si_tmpl.is_product_active)
        self.assertTrue(self.si_variant.is_product_active)

    def test_archive_template_deactivates_all_supplierinfo(self):
        """Archiving a template should deactivate all its supplierinfo records."""
        self.template.write({"active": False})
        self.assertFalse(self.si_tmpl.is_product_active)
        self.assertFalse(self.si_variant.is_product_active)

    def test_unarchive_template_reactivates_all_supplierinfo(self):
        """Unarchiving a template should reactivate all its supplierinfo records."""
        self.template.write({"active": False})
        self.template.with_context(active_test=False).write({"active": True})
        self.assertTrue(self.si_tmpl.is_product_active)
        self.assertTrue(self.si_variant.is_product_active)

    def test_archive_variant_deactivates_variant_supplierinfo_only(self):
        """Archiving a variant should deactivate only its supplierinfo record,
        not the template-level one."""
        self.variant.write({"active": False})
        self.assertFalse(self.si_variant.is_product_active)
        # Template-level supplierinfo is unaffected — template is still active.
        self.assertTrue(self.si_tmpl.is_product_active)

    def test_unarchive_variant_reactivates_variant_supplierinfo(self):
        """Unarchiving a variant should reactivate only its supplierinfo record."""
        self.variant.write({"active": False})
        self.variant.with_context(active_test=False).write({"active": True})
        self.assertTrue(self.si_variant.is_product_active)
