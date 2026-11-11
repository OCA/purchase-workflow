# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon

from .. import __manifest__


@tagged("post_install", "-at_install")
class TestPurchase(BaseCommon):
    _test_user_groups = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product_order = cls.env["product.product"].create(
            {
                "name": "Zed+ Antivirus",
                "standard_price": 235.0,
                "list_price": 280.0,
                "type": "consu",
                "uom_id": uom_unit.id,
                "purchase_method": "purchase",
                "default_code": "PROD_ORDER",
                "taxes_id": False,
            }
        )
        cls.partner_a = cls.env["res.partner"].create(
            {
                "name": "partner_a",
                "company_id": False,
                "purchase_note": "Purchase Default Terms and Conditions Partner",
            }
        )
        cls.company_id = cls.env["res.company"].create(
            {
                "name": "Test Company",
                "country_id": cls.env.ref("base.be").id,
                "purchase_note": "Company Default Terms and Conditions",
            }
        )

    def test_manifest_version(self):
        self.assertTrue(__manifest__.__file__.endswith("__manifest__.py"))

    def test_partner_note_with_form(self):
        company_note = "Company Default Terms and Conditions"
        self.company_id.purchase_note = company_note

        # First case: Test with partner's purchase note
        with Form(self.env["purchase.order"]) as purchase_form:
            purchase_form.partner_id = self.partner_a
            purchase_form.company_id = self.company_id

            self.assertEqual(
                purchase_form.note.strip(),
                self.partner_a.purchase_note,
                "Notes should be set from partner's purchase note",
            )

        # Second case: Clear the partner's purchase note and test company purchase note
        self.partner_a.purchase_note = False
        self.env["ir.config_parameter"].sudo().set_bool(
            "purchase.use_purchase_note", True
        )

        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "company_id": self.company_id.id,
            }
        )
        purchase_order.onchange_partner_id()

        with Form(purchase_order) as purchase_form:
            self.assertIn(
                company_note,
                purchase_form.note,
                "Notes should contain company purchase note when partner note is empty",
            )

    def test_onchange_no_partner_note_and_setting_disabled(self):
        """Test note is cleared when partner has no note and setting is off."""
        self.env["ir.config_parameter"].sudo().set_bool(
            "purchase.use_purchase_note", False
        )
        partner_b = self.env["res.partner"].create({"name": "Partner B"})

        with Form(self.env["purchase.order"]) as po_form:
            po_form.partner_id = self.partner_a
            self.assertEqual(po_form.note.strip(), self.partner_a.purchase_note)

            # Change to a partner without a note
            po_form.partner_id = partner_b

            # The note should be cleared
            self.assertFalse(po_form.note)
