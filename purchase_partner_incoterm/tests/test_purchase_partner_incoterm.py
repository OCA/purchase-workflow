from odoo.tests.common import TransactionCase


class TestPurchasePartnerIncoterm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_obj = cls.env["res.partner"]
        cls.po_model = cls.env["purchase.order"]
        # Create a partner with incoterm details
        cls.partner = cls.partner_obj.create(
            {
                "name": "Test Partner",
                "purchase_incoterm_id": cls.env.ref("account.incoterm_EXW").id,
                "purchase_incoterm_address_id": cls.partner_obj.create(
                    {
                        "name": "Incoterm Address",
                    }
                ).id,
            }
        )
        # Create a purchase order
        cls.purchase_order = cls.po_model.create(
            {
                "partner_id": cls.partner.id,
            }
        )

    def test_onchange_partner_id(self):
        # Trigger the onchange method
        self.purchase_order.onchange_partner_id()
        # Check if the incoterm fields are set correctly
        self.assertEqual(
            self.purchase_order.incoterm_id, self.partner.purchase_incoterm_id
        )
        self.assertEqual(
            self.purchase_order.incoterm_address_id,
            self.partner.purchase_incoterm_address_id,
        )

    def test_automated_po_creation(self):
        auto_po = self.po_model.create({"partner_id": self.partner.id})
        self.assertEqual(auto_po.incoterm_id, self.partner.purchase_incoterm_id)
        self.assertEqual(
            auto_po.incoterm_address_id, self.partner.purchase_incoterm_address_id
        )

    def test_user_override_preserved(self):
        custom_incoterm = self.env.ref("account.incoterm_FCA")
        po_with_custom = self.po_model.create(
            {
                "partner_id": self.partner.id,
                "incoterm_id": custom_incoterm.id,
            }
        )
        self.assertEqual(po_with_custom.incoterm_id, custom_incoterm)
