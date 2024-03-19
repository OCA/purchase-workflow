# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPurchaseSupplierInfoPackaging(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Packaging = cls.env["product.packaging"]
        cls.Partner = cls.env["res.partner"]
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]
        cls.SupplierInfo = cls.env["product.supplierinfo"]
        cls.product_chair = cls.env.ref("product.product_delivery_01")

        cls.supplier = cls.Partner.create(
            {
                "name": "Supplier",
            }
        )

        cls.packaging_chair = cls.Packaging.create(
            {
                "product_id": cls.product_chair.id,
                "name": "Pallet of 10 chair",
                "qty": 10,
            }
        )

        cls.supplier_info_chair = cls.SupplierInfo.create(
            {
                "product_id": cls.product_chair.id,
                "packaging_id": cls.packaging_chair.id,
                "partner_id": cls.supplier.id,
                "min_qty": 30,
                "packaging_min_qty": 3,
            }
        )

    def test_po_line_packaging_qty(self):
        order = self.PurchaseOrder.create(
            {
                "partner_id": self.supplier.id,
            }
        )

        line = self.PurchaseOrderLine.create(
            {
                "order_id": order.id,
                "product_id": self.product_chair.id,
            }
        )

        self.assertEqual(
            line.product_qty,
            30,
        )
        self.assertEqual(line.product_packaging_id, self.packaging_chair)
        self.assertEqual(line.product_packaging_qty, 3)
