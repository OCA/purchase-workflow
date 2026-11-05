# ?? 2021 Solvos Consultor??a Inform??tica (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestPurchaseOrderTypeDashboard(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_obj = cls.env["purchase.order"]

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

    def test_purchase_order_type_dashboard(self):
        po_type1_rfq_count = self.type1.state_rfq_po_count
        purchase = self._create_purchase(
            [
                (self.product_storage_box, 1),
                (self.product_pedal_bin, 5),
                (self.product_conference_chair, 8),
            ]
        )
        self.assertEqual(self.type1.state_rfq_po_count, po_type1_rfq_count + 1)

        purchase.button_confirm()
        po_type1_is_no_count = self.type1.invoice_status_no_po_count
        po_type1_is_ti_count = self.type1.invoice_status_ti_po_count
        purchase.order_line[0].qty_received = 1.0
        self.assertEqual(
            self.type1.invoice_status_no_po_count, po_type1_is_no_count - 1
        )
        self.assertEqual(
            self.type1.invoice_status_ti_po_count, po_type1_is_ti_count + 1
        )

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
