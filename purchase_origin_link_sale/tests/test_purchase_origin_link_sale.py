from odoo.tests.common import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseOriginLinkSale(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOriginLinkSale, cls).setUpClass()
        vendor = cls.env["res.partner"].create({"name": "Partner #2"})
        supplierinfo = cls.env["product.supplierinfo"].create({"name": vendor.id})
        cls.product = cls.env["product.product"].create(
            {"name": "Product Test", "seller_ids": [(6, 0, [supplierinfo.id])]}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner #1"})

    def test_01_purchase_origin_link_sale(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": self.product.list_price,
                            "name": self.product.name,
                        },
                    )
                ],
            }
        )
        sale_order.with_context(test_enabled=True).action_confirm()

        vals = {"partner_id": self.partner.id, "origin": str(sale_order.name)}

        purchase_order = self.env["purchase.order"].create(vals)

        self.assertTrue(type(purchase_order.origin_reference), self.env["sale.order"])
        self.assertTrue(purchase_order.origin_reference, sale_order.id)
