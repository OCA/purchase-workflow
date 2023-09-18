# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import ValidationError

from .common import Common


class TestPackagingTypeCanBePurchased(Common):
    @classmethod
    def setUpClassPurchaseOrder(cls):
        super().setUpClassPurchaseOrder()
        cls.order_line.product_qty = 3.0

    def test_packaging_type_can_be_purchased(self):
        self.order_line.write({"product_packaging": self.packaging_tu.id})
        with self.assertRaises(ValidationError):
            self.order_line.write(
                {"product_packaging": self.packaging_cannot_be_purchased.id}
            )
            onchange_res = self.order_line._onchange_product_packaging()
            self.assertIn("warning", onchange_res)

    def test_product_packaging_can_be_purchased(self):
        """Check that a product.packaging can be independently set as can be purchased."""
        exception_msg = (
            "Packaging Test packaging cannot be purchased on product {} must be set "
            "as 'Can be purchased' in order to be used on a purchase order."
        ).format(self.product.name)
        with self.assertRaisesRegex(ValidationError, exception_msg):
            self.order_line.write(
                {"product_packaging": self.packaging_cannot_be_purchased.id}
            )
        # Packaging can be purchased even if the packaging type does not allows it
        self.packaging_cannot_be_purchased.can_be_purchased = True
        self.order_line.write(
            {"product_packaging": self.packaging_cannot_be_purchased.id}
        )
        # Changing the packaging type on product.packaging updates can_be_purchased
        self.purchaseable_packagings.unlink()
        self.packaging_cannot_be_purchased.packaging_type_id = self.packaging_type_tu
        self.packaging_cannot_be_purchased.packaging_type_id = (
            self.packaging_type_cannot_be_purchased
        )
        self.assertEqual(self.packaging_cannot_be_purchased.can_be_purchased, False)
        # Changing the can_be_purchased on the packaging_type does not update the packaging
        self.packaging_type_cannot_be_purchased.can_be_purchased = True
        self.assertEqual(self.packaging_cannot_be_purchased.can_be_purchased, False)
