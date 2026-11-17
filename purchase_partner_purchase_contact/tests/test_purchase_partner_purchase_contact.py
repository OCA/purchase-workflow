# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestPurchasePartnerPurchaseContact(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_company = cls.env["res.partner"].create(
            {
                "name": "Test Vendor",
                "is_company": True,
            }
        )
        cls.contact_person_1 = cls.env["res.partner"].create(
            {
                "name": "John Doe",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "contact",
            }
        )
        cls.contact_person_2 = cls.env["res.partner"].create(
            {
                "name": "Jane Smith",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "contact",
            }
        )
        cls.purchase_contact = cls.env["res.partner"].create(
            {
                "name": "Pat Purchasing",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "purchase",
                "email": "pat@example.com",
            }
        )
        cls.purchase_contact_no_email = cls.env["res.partner"].create(
            {
                "name": "Sam No-Email",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "purchase",
            }
        )
        cls.other_company = cls.env["res.partner"].create(
            {
                "name": "Other Vendor",
                "is_company": True,
            }
        )

    def _new_order(self, **vals):
        vals.setdefault("partner_id", self.partner_company.id)
        return self.env["purchase.order"].create(vals)

    def test_01_purchase_order_contact_field(self):
        """The purchase contact field can be set on a purchase order."""
        order = self._new_order(purchase_contact_partner_id=self.contact_person_1.id)
        self.assertEqual(order.purchase_contact_partner_id, self.contact_person_1)

    def test_02_onchange_partner_clears_contact(self):
        """Changing the partner clears an incompatible purchase contact."""
        order = self._new_order(purchase_contact_partner_id=self.contact_person_1.id)
        order.partner_id = self.other_company
        order._onchange_partner_id_clear_purchase_contact()
        self.assertFalse(order.purchase_contact_partner_id)

    def test_03_onchange_keeps_compatible_contact(self):
        """A contact still in the partner's hierarchy is kept on onchange."""
        order = self._new_order(purchase_contact_partner_id=self.contact_person_1.id)
        order._onchange_partner_id_clear_purchase_contact()
        self.assertEqual(order.purchase_contact_partner_id, self.contact_person_1)

    def test_04_empty_contact_allowed(self):
        """The purchase contact field can be left empty."""
        order = self._new_order()
        self.assertFalse(order.purchase_contact_partner_id)

    def test_05_multiple_orders_different_contacts(self):
        """Different orders can carry different contacts."""
        order_1 = self._new_order(purchase_contact_partner_id=self.contact_person_1.id)
        order_2 = self._new_order(purchase_contact_partner_id=self.contact_person_2.id)
        self.assertEqual(order_1.purchase_contact_partner_id, self.contact_person_1)
        self.assertEqual(order_2.purchase_contact_partner_id, self.contact_person_2)

    def test_06_auto_switch_contact_to_company(self):
        """Selecting a contact as partner_id promotes it to the root company."""
        order = self._new_order()
        order.partner_id = self.contact_person_1
        switched = order._purchase_contact_apply_auto_switch()
        self.assertTrue(switched)
        self.assertEqual(order.partner_id, self.partner_company)
        self.assertEqual(order.purchase_contact_partner_id, self.contact_person_1)

    def test_08_purchase_type_contact(self):
        """A 'purchase' address type exists and such a contact can be set."""
        self.assertIn(
            "purchase",
            dict(self.env["res.partner"]._fields["type"].selection),
        )
        order = self._new_order(purchase_contact_partner_id=self.purchase_contact.id)
        self.assertEqual(order.purchase_contact_partner_id, self.purchase_contact)
        self.assertEqual(order.purchase_contact_partner_id.type, "purchase")

    def test_09_mail_default_recipient_is_contact(self):
        """The default mail recipient is the purchase contact (with email)."""
        order = self._new_order(purchase_contact_partner_id=self.purchase_contact.id)
        self.assertEqual(order._mail_get_partners()[order.id], self.purchase_contact)

    def test_10_mail_fallback_to_vendor(self):
        """Falls back to the vendor when the contact has no email or is unset."""
        order_no_email = self._new_order(
            purchase_contact_partner_id=self.purchase_contact_no_email.id
        )
        self.assertEqual(
            order_no_email._mail_get_partners()[order_no_email.id],
            self.partner_company,
        )
        order_no_contact = self._new_order()
        self.assertEqual(
            order_no_contact._mail_get_partners()[order_no_contact.id],
            self.partner_company,
        )

    def test_07_onchange_keeps_grandchild_contact(self):
        """A grandchild contact is not cleared: it belongs to the hierarchy."""
        department = self.env["res.partner"].create(
            {
                "name": "Purchase Department",
                "is_company": False,
                "parent_id": self.partner_company.id,
                "type": "contact",
            }
        )
        grandchild = self.env["res.partner"].create(
            {
                "name": "Grandchild Contact",
                "is_company": False,
                "parent_id": department.id,
                "type": "contact",
            }
        )
        order = self._new_order(purchase_contact_partner_id=grandchild.id)
        order._onchange_partner_id_clear_purchase_contact()
        self.assertEqual(order.purchase_contact_partner_id, grandchild)
