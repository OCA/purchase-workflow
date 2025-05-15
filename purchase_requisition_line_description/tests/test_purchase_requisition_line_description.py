# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestPurchaseRequisitionLineDescription(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "standard_price": 10,
                "description_purchase": "description for purchase",
            }
        )

    def test_compute_product_description_name(self):
        """Test that product description is computed using product and vendor."""
        requisition = self.env["purchase.requisition"].create(
            {
                "vendor_id": self.partner.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                        },
                    )
                ],
            }
        )
        expected_description = (
            f"{self.product.name}\n{self.product.description_purchase}"
        )
        self.assertEqual(requisition.line_ids[0].name, expected_description)
