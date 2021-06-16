# Copyright 2017 Roberto Onnis - innoviu
# Copyright 2021 Alfredo Zamora - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import fields
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestProductCustomerCodePurchase(TransactionCase):
    def setUp(self):
        super(TestProductCustomerCodePurchase, self).setUp()
        # Useful models
        self.res_partner = self.env["res.partner"]
        self.purchase_order = self.env["purchase.order"]
        self.purchase_order_line = self.env["purchase.order.line"]
        self.product_customerinfo = self.env["product.customerinfo"]
        self.product_code = "code01"

    def _create_partner(self, name):
        return self.res_partner.create(
            {"name": name, "email": "example@yourcompany.com", "phone": 123456}
        )

    def _create_product_customerinfo(self, partner, product):
        return self.product_customerinfo.create(
            {
                "name": partner.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_code": self.product_code,
            }
        )

    def _create_purchase_order(self, partner, product):
        po = Form(self.env["purchase.order"])
        po.partner_id = partner
        with po.order_line.new() as po_line:
            po_line.product_id = product
            po_line.product_qty = 1.0
            po_line.price_unit = 100
            po_line.date_planned = fields.Datetime.now()
        return po.save()

    def test_00_purchase_customer_code(self):
        partner_id = self._create_partner("Partner Test")
        product_id = self.env.ref("product.product_product_6")
        self._create_product_customerinfo(partner_id, product_id)
        self.po = self._create_purchase_order(partner_id, product_id)
        self.assertTrue(self.po, "No purchase order created")
        self.assertTrue(self.po.order_line, "No purchase order line created")
        self.assertEqual(
            self.po.order_line.product_customer_code,
            self.product_code,
            "PO line customer code should be '%s'" % self.product_code,
        )
