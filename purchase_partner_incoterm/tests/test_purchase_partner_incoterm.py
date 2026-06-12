from odoo import fields
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
                "purchase_incoterm_location": "Test Location",
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
        self.assertEqual(
            self.purchase_order.incoterm_location,
            self.partner.purchase_incoterm_location,
        )

    def test_prepare_purchase_order_from_stock_rule_sets_incoterm_fields(self):
        product = self.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "consu",
            }
        )
        supplier = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "min_qty": 1.0,
                "delay": 1,
                "price": 10.0,
            }
        )
        stock_rule = self.env["stock.rule"].search(
            [
                ("action", "=", "buy"),
                ("company_id", "=", self.env.company.id),
                ("picking_type_id", "!=", False),
            ],
            limit=1,
        )
        self.assertTrue(stock_rule, "Expected at least one buy stock rule")

        values = [
            {
                "supplier": supplier,
                "date_planned": fields.Datetime.to_string(fields.Datetime.now()),
                "reference_ids": self.env["stock.reference"],
            }
        ]
        po_vals = stock_rule._prepare_purchase_order(
            self.env.company,
            ["Test Origin"],
            values,
        )

        self.assertEqual(po_vals.get("incoterm_id"), self.incoterm.id)
        self.assertEqual(po_vals.get("incoterm_address_id"), self.incoterm_address.id)
        self.assertEqual(po_vals.get("incoterm_location"), "Test Location")
