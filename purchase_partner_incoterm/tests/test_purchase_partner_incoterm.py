from odoo.tests.common import TransactionCase


class TestPurchasePartnerIncoterm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_obj = cls.env["res.partner"]
        cls.po_model = cls.env["purchase.order"]
        cls.incoterm_model = cls.env["account.incoterms"]

        # Create dummy incoterm
        cls.incoterm = cls.incoterm_model.create(
            {
                "code": "EXW",
                "name": "EX WORKS",
            }
        )

        # Create an address for incoterm
        cls.incoterm_address = cls.partner_obj.create(
            {
                "name": "Incoterm Address",
            }
        )

        # Create a partner with incoterm details
        cls.partner = cls.partner_obj.create(
            {
                "name": "Test Partner",
                "purchase_incoterm_id": cls.incoterm.id,
                "purchase_incoterm_address_id": cls.incoterm_address.id,
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
