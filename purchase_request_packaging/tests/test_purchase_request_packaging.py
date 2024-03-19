# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPurchaseRequestPackaging(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PrToPo = cls.env["purchase.request.line.make.purchase.order"]
        cls.Packaging = cls.env["product.packaging"]
        cls.Partner = cls.env["res.partner"]
        cls.Product = cls.env["product.product"]
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]
        cls.PurchaseRequest = cls.env["purchase.request"]
        cls.PurchaseRequestLine = cls.env["purchase.request.line"]
        cls.SupplierInfo = cls.env["product.supplierinfo"]

        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        cls.product_chair = cls.Product.create(
            {
                "name": "Rocking chair",
                "purchase_method": "purchase",
                "uom_id": cls.uom_unit.id,
            }
        )

        cls.product_lamp = cls.Product.create(
            {
                "name": "Lamp",
                "purchase_method": "purchase",
                "uom_id": cls.uom_unit.id,
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

        cls.packaging_lamp = cls.Packaging.create(
            {
                "product_id": cls.product_lamp.id,
                "name": "Box of 8 lamps",
                "qty": 8,
            }
        )

    def test_pr_line_packaging(self):
        request = self.PurchaseRequest.create({})
        chair = self.product_chair
        line = self.PurchaseRequestLine.create(
            {
                "request_id": request.id,
                "product_id": chair.id,
            }
        )
        line.onchange_product_id()
        line.product_qty = 30

        self.assertEqual(line.product_packaging_id, self.packaging_chair)
        self.assertEqual(line.product_packaging_qty, 3)
        self.assertEqual(
            line.product_packaging_id_domain,
            [
                ("purchase", "=", True),
                ("product_id", "=", chair.id),
                "|",
                ("company_id", "=", self.env.user.company_id.id),
                ("company_id", "=", False),
            ],
        )

        line.product_packaging_qty = 5
        line._onchange_product_packaging_qty_load_product_qty()
        self.assertEqual(line.product_qty, 50)

    def test_pr_line_wrong_packaging(self):
        request = self.PurchaseRequest.create({})
        line = self.PurchaseRequestLine.create(
            {
                "request_id": request.id,
                "product_id": self.product_chair.id,
            }
        )
        line.onchange_product_id()

        with self.assertRaises(ValidationError) as exc:
            line.product_packaging_id = self.packaging_lamp
        self.assertIn("is not linked to current product", exc.exception.args[0])

    def test_pr_to_po(self):
        request = self.PurchaseRequest.create({})
        line = self.PurchaseRequestLine.create(
            {
                "request_id": request.id,
                "product_id": self.product_chair.id,
            }
        )
        line.onchange_product_id()
        line.product_qty = 5
        line.product_packaging_id = self.packaging_chair

        self.assertEqual(line.product_packaging_qty, 0.5)

        request.button_to_approve()
        request.button_approved()

        wizard = self.PrToPo.with_context(
            active_model=request._name, active_ids=request.ids
        ).create(
            {
                "supplier_id": self.supplier.id,
            }
        )

        res = wizard.make_purchase_order()
        order = self.PurchaseOrder.search(res["domain"])
        order_line = order.order_line

        self.assertEqual(len(order_line), 1)
        self.assertEqual(order_line.product_packaging_id, self.packaging_chair)
        self.assertEqual(order_line.product_packaging_qty, 0.5)
