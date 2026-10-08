from odoo.tests import Form, TransactionCase


class TestPurchaseCommercialPartner(TransactionCase):
    def test_purchase_commercial_partner(self):
        """The commercial partner is derived from the partner of the PO"""
        partner = self.env["res.partner"].create(
            {
                "name": "Megacorps",
                "is_company": True,
            }
        )
        contact = self.env["res.partner"].create(
            {
                "name": "Pip",
                "is_company": False,
                "parent_id": partner.id,
            }
        )
        po_form = Form(self.env["purchase.order"])
        po_form.partner_id = contact
        self.assertEqual(po_form.commercial_partner_id, partner)
