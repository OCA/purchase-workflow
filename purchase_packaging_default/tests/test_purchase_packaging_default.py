# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.product.tests.common import ProductCommon


class PurchasePackagingDefault(ProductCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("product.group_stock_packaging")
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env
        cls.config = cls.env["res.config.settings"].create({})
        cls.config.purchase_packaging_default_enabled = True
        cls.config.set_values()
        with Form(cls.product) as product_f:
            with product_f.packaging_ids.new() as packaging_f:
                packaging_f.sequence = 1
                packaging_f.name = "Pallet"
                packaging_f.qty = 240
                packaging_f.purchase = True
            with product_f.packaging_ids.new() as packaging_f:
                packaging_f.sequence = 2
                packaging_f.name = "Big Box"
                packaging_f.qty = 24
                packaging_f.purchase = True
        cls.pallet, cls.big_box = cls.product.packaging_ids

    def test_purchase_packaging_default(self):
        po_f = Form(self.env["purchase.order"])
        po_f.partner_id = self.partner
        with po_f.order_line.new() as line_f:
            line_f.product_id = self.product
            line_f.product_qty = 120
            # We take the first available packaging
            self.assertEqual(line_f.product_packaging_id, self.pallet)
            # Packaging qty is round up to 1
            self.assertEqual(line_f.product_packaging_qty, 1)
            # Packaging qty is round up to 2
            line_f.product_qty = 241
            self.assertEqual(line_f.product_packaging_qty, 2)

    def test_purchase_packaging_default_enabled_disabled(self):
        """Test default packing behaviour with setting disabled/enabled"""
        self.config.purchase_packaging_default_enabled = False
        new_po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 120,
                        },
                    )
                ],
            }
        )
        # Standard behaviour: With setting disabled, the default value
        # try find a packaging's qty in given uom which a divisor of
        # the given product_qty. If so, return the one with greatest divisor.
        self.assertEqual(new_po.order_line.product_packaging_id, self.big_box)

        self.config.purchase_packaging_default_enabled = True
        new_po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 120,
                        },
                    )
                ],
            }
        )
        # The default value is the first of the packaging sequence
        self.assertEqual(new_po.order_line.product_packaging_id, self.pallet)
