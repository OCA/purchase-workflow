# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestPurchaseOrderType(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_obj = cls.env["purchase.order"]
        cls.company_obj = cls.env["res.company"]

        # Partner
        cls.partner1 = cls.env["res.partner"].create(
            {
                "name": "Wood Corner",
                "is_company": True,
                "street": "1839 Arbor Way",
                "city": "Turlock",
                "email": "wood.corner26@example.com",
                "phone": "(623)-853-7197",
            }
        )

        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "Deco Addict",
                "is_company": True,
                "street": "77 Santa Barbara Rd",
                "city": "Pleasant Hill",
                "email": "deco_addict@yourcompany.example.com",
                "phone": "(603)-996-3829",
            }
        )

        cls.category_office = cls.env["product.category"].create(
            {
                "name": "Office Furniture",
            }
        )

        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        # Products
        cls.product_storage_box = cls.env["product.product"].create(
            {
                "name": "Storage Box",
                "categ_id": cls.category_office.id,
                "standard_price": 14.0,
                "list_price": 15.8,
                "type": "consu",
                "uom_id": cls.uom_unit.id,
                "default_code": "E-COM08",
            }
        )

        cls.product_pedal_bin = cls.env["product.product"].create(
            {
                "name": "Pedal Bin",
                "categ_id": cls.category_office.id,
                "standard_price": 10.0,
                "list_price": 47.0,
                "type": "consu",
                "uom_id": cls.uom_unit.id,
                "default_code": "E-COM10",
            }
        )

        cls.product_conference_chair = cls.env["product.product"].create(
            {
                "name": "Conference Chair",
                "categ_id": cls.category_office.id,
                "standard_price": 28.0,
                "list_price": 33.0,
                "type": "consu",
                "uom_id": cls.uom_unit.id,
                "default_code": "E-COM12",
            }
        )

        # Purchase Type
        cls.type1 = cls.env["purchase.order.type"].create(
            {
                "name": "Regular",
            }
        )

        cls.type2 = cls.env["purchase.order.type"].create(
            {
                "name": "Planned",
            }
        )

        # Payment Term
        cls.payterm = cls.env["account.payment.term"].create({"name": "Immediate"})
        # Incoterm (safe fallback if account not loaded)
        if "account.incoterm" in cls.env:
            cls.incoterm = cls.env["account.incoterm"].create(
                {
                    "code": "EXW",
                    "name": "Ex Works",
                }
            )
        else:
            cls.incoterm = False
        cls.type2.payment_term_id = cls.payterm
        cls.type2.incoterm_id = cls.incoterm if cls.incoterm else False
        cls.partner1.purchase_type = cls.type2
        cls.company2 = cls.company_obj.create({"name": "company2"})

    def test_purchase_order_type(self):
        purchase = self._create_purchase(
            [
                (self.product_storage_box, 1),
                (self.product_pedal_bin, 5),
                (self.product_conference_chair, 8),
            ]
        )
        self.assertEqual(purchase.order_type, self.type1)
        self.assertFalse(purchase.incoterm_id)
        self.assertFalse(purchase.payment_term_id)
        purchase.onchange_partner_id()
        self.assertEqual(purchase.order_type, self.type2)
        purchase.onchange_order_type()
        if self.incoterm:
            self.assertEqual(purchase.incoterm_id, self.incoterm)
        else:
            self.assertFalse(purchase.incoterm_id)

        self.assertEqual(purchase.payment_term_id, self.payterm)

    def _create_purchase(self, line_products):
        """Create a purchase order.
        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        for product, qty in line_products:
            line_values = {
                "name": product.name,
                "product_id": product.id,
                "product_qty": qty,
                "product_uom_id": product.uom_id.id,
                "price_unit": 100,
                "date_planned": fields.Datetime.now(),
            }
            lines.append((0, 0, line_values))
        purchase = self.po_obj.create(
            {
                "partner_id": self.partner1.id,
                "order_type": self.type1.id,
                "order_line": lines,
            }
        )
        return purchase

    def test_purchase_order_change_company(self):
        order = self.po_obj.create({"partner_id": self.partner1.id})
        order.onchange_partner_id()
        self.assertEqual(order.order_type, self.type2)
        order._onchange_company()
        self.assertEqual(order.order_type, self.type2)
        order.order_type = False
        order._onchange_company()
        self.assertEqual(order.order_type, order._default_order_type())

    def test_purchase_order_type_company_error(self):
        order = self.po_obj.create(
            {
                "partner_id": self.partner1.id,
                "order_type": self.type1.id,
            }
        )
        self.assertEqual(order.order_type, self.type1)
        self.assertEqual(order.company_id, self.type1.company_id)
        with self.assertRaises(ValidationError):
            order.write({"company_id": self.company2.id})

    def test_order_type_from_partner(self):
        """Test order type behavior when changing partners"""
        lines = [
            (
                0,
                0,
                {
                    "name": self.product_conference_chair.name,
                    "product_id": self.product_conference_chair.id,
                    "product_qty": 3,
                    "product_uom_id": self.product_conference_chair.uom_id.id,
                    "price_unit": 100,
                    "date_planned": fields.Datetime.now(),
                },
            )
        ]

        type_from_partner = self.po_obj.create(
            {
                "partner_id": self.partner1.id,
                "order_type": self.type1.id,
                "order_line": lines,
            }
        )

        type_from_partner.onchange_partner_id()
        self.assertEqual(type_from_partner.order_type, self.partner1.purchase_type)

        # Test: changing partner doesn't override existing order_type
        self.partner2.purchase_type = self.type1
        type_from_partner.partner_id = self.partner2
        self.assertNotEqual(type_from_partner.order_type, self.partner2.purchase_type)

        # Check if order_type of sale has not deleted
        self.partner2.purchase_type = False
        type_from_partner.write({"partner_id": self.partner1})
        type_from_partner.write({"partner_id": self.partner2})
        self.assertEqual(type_from_partner.order_type, self.type2)

        # Check if set order_type on sale again
        type_from_partner.write({"partner_id": self.partner1})
        type_from_partner.write({"order_type": False})
        type_from_partner.write({"partner_id": self.partner2})
        type_from_partner.write({"partner_id": self.partner2})
        self.assertEqual(type_from_partner.order_type, self.partner2.purchase_type)
