# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPurchaseStockSupplierInfoPackaging(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Packaging = cls.env["product.packaging"]
        cls.Partner = cls.env["res.partner"]
        cls.ProcurementGroup = cls.env["procurement.group"]
        cls.Product = cls.env["product.product"]
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]
        cls.Orderpoint = cls.env["stock.warehouse.orderpoint"]
        cls.SupplierInfo = cls.env["product.supplierinfo"]
        cls.WizardReplenish = cls.env["product.replenish"]

        cls.product_chair = cls.Product.create(
            {
                "name": "Rocking chair",
                "purchase_method": "purchase",
            }
        )

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

        cls.orderpoint_chair = cls.Orderpoint.create(
            {
                "product_id": cls.product_chair.id,
                "product_min_qty": 60,
            }
        )

    def test_po_line_packaging_qty(self):
        self.ProcurementGroup.run_scheduler()

        po = self.PurchaseOrder.search(
            [
                ("partner_id", "=", self.supplier.id),
            ],
            limit=1,
        )

        self.assertTrue(bool(po))

        line = po.order_line[0]
        self.assertEqual(line.product_packaging_id, self.packaging_chair)
        self.assertEqual(line.product_packaging_qty, 6)
        self.assertEqual(line.product_qty, 60)
