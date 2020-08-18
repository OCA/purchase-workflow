# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import time

from odoo.exceptions import ValidationError
from odoo.tests import common, tagged
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


@tagged("post_install", "-at_install")
class TestPurchaseOrderType(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_obj = cls.env["purchase.order"]
        cls.company_obj = cls.env["res.company"]
        # Partner
        cls.partner1 = cls.env.ref("base.res_partner_1")
        # Products
        cls.product1 = cls.env.ref("product.product_product_7")
        cls.product2 = cls.env.ref("product.product_product_9")
        cls.product3 = cls.env.ref("product.product_product_11")
        # Purchase Type
        cls.type1 = cls.env.ref("purchase_order_type.po_type_regular")
        cls.type2 = cls.env.ref("purchase_order_type.po_type_planned")
        # Payment Term
        cls.payterm = cls.env.ref("account.account_payment_term_immediate")
        # Incoterm
        cls.incoterm = cls.env.ref("account.incoterm_EXW")
        cls.type2.payment_term_id = cls.payterm
        cls.type2.incoterm_id = cls.incoterm
        cls.partner1.purchase_type = cls.type2
        cls.company2 = cls.company_obj.create({"name": "company2"})

    def test_purchase_order_type(self):
        purchase = self._create_purchase(
            [(self.product1, 1), (self.product2, 5), (self.product3, 8)]
        )
        self.assertEquals(purchase.order_type, self.type1)
        self.assertFalse(purchase.incoterm_id)
        self.assertFalse(purchase.payment_term_id)
        purchase.onchange_partner_id()
        self.assertEquals(purchase.order_type, self.type2)
        purchase.onchange_order_type()
        self.assertEquals(purchase.incoterm_id, self.incoterm)
        self.assertEquals(purchase.payment_term_id, self.payterm)

    def _create_purchase(self, line_products):
        """ Create a purchase order.
        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        for product, qty in line_products:
            line_values = {
                "name": product.name,
                "product_id": product.id,
                "product_qty": qty,
                "product_uom": product.uom_id.id,
                "price_unit": 100,
                "date_planned": time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
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
        order = self.po_obj.new({"partner_id": self.partner1.id})
        self.assertEqual(order.order_type, self.type1)
        order._onchange_company()
        self.assertFalse(order.order_type)

    def test_purchase_order_type_company_error(self):
        order = self.po_obj.create({"partner_id": self.partner1.id})
        self.assertEqual(order.order_type, self.type1)
        self.assertEqual(order.company_id, self.type1.company_id)
        with self.assertRaises(ValidationError):
            order.write({"company_id": self.company2.id})
