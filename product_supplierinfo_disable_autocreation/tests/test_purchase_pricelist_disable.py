from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestPurchasePricelistDisable(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )

        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "type": "product",
            }
        )

        cls.partner1 = cls.env["res.partner"].create(
            {
                "name": "Vendor with auto pricelist",
            }
        )

        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "Vendor without auto pricelist",
            }
        )

        cls.company2 = cls.env["res.company"].create(
            {
                "name": "Test Company",
            }
        )

        # Create purchase orders and lines for reuse in tests
        cls.po1 = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner1.id,
            }
        )
        cls.env["purchase.order.line"].create(
            {
                "order_id": cls.po1.id,
                "product_id": cls.product.id,
                "product_qty": 1.0,
                "price_unit": 100.0,
                "name": "Test Line",
                "product_uom": cls.product.uom_id.id,
            }
        )

        cls.po2 = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner2.id,
            }
        )
        cls.env["purchase.order.line"].create(
            {
                "order_id": cls.po2.id,
                "product_id": cls.product.id,
                "product_qty": 1.0,
                "price_unit": 100.0,
                "name": "Test Line",
                "product_uom": cls.product.uom_id.id,
            }
        )

        # Purchase order with multiple product lines
        cls.po_multi1 = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner1.id,
            }
        )
        cls.env["purchase.order.line"].create(
            [
                {
                    "order_id": cls.po_multi1.id,
                    "product_id": cls.product.id,
                    "product_qty": 1.0,
                    "price_unit": 100.0,
                    "name": "Test Line 1",
                    "product_uom": cls.product.uom_id.id,
                },
                {
                    "order_id": cls.po_multi1.id,
                    "product_id": cls.product2.id,
                    "product_qty": 2.0,
                    "price_unit": 150.0,
                    "name": "Test Line 2",
                    "product_uom": cls.product2.uom_id.id,
                },
            ]
        )

        cls.po_multi2 = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner2.id,
            }
        )
        cls.env["purchase.order.line"].create(
            [
                {
                    "order_id": cls.po_multi2.id,
                    "product_id": cls.product.id,
                    "product_qty": 1.0,
                    "price_unit": 100.0,
                    "name": "Test Line 1",
                    "product_uom": cls.product.uom_id.id,
                },
                {
                    "order_id": cls.po_multi2.id,
                    "product_id": cls.product2.id,
                    "product_qty": 2.0,
                    "price_unit": 150.0,
                    "name": "Test Line 2",
                    "product_uom": cls.product2.uom_id.id,
                },
            ]
        )

    def test_01_pricelist_enabled(self):
        """Test supplier pricelist creation when enabled"""
        self.env.company.purchase_pricelist_disable_autocreate = True

        seller_count_before = len(self.product.seller_ids)
        self.po1.button_confirm()
        seller_count_after = len(self.product.seller_ids)

        self.assertEqual(seller_count_after, seller_count_before + 1)
        self.assertIn(self.partner1, self.product.seller_ids.mapped("partner_id"))

    def test_02_pricelist_disabled(self):
        """Test supplier pricelist creation when disabled"""
        self.env.company.purchase_pricelist_disable_autocreate = False

        seller_count_before = len(self.product.seller_ids)
        self.po2.button_confirm()
        seller_count_after = len(self.product.seller_ids)

        self.assertEqual(seller_count_after, seller_count_before)
        self.assertNotIn(self.partner2, self.product.seller_ids.mapped("partner_id"))

    def test_03_multiple_products_pricelist_enabled(self):
        """Test multiple supplier pricelists creation when enabled"""
        self.env.company.purchase_pricelist_disable_autocreate = True

        seller_count_before_1 = len(self.product.seller_ids)
        seller_count_before_2 = len(self.product2.seller_ids)

        self.po_multi1.button_confirm()

        seller_count_after_1 = len(self.product.seller_ids)
        seller_count_after_2 = len(self.product2.seller_ids)

        self.assertEqual(seller_count_after_1, seller_count_before_1 + 1)
        self.assertEqual(seller_count_after_2, seller_count_before_2 + 1)
        self.assertIn(self.partner1, self.product.seller_ids.mapped("partner_id"))
        self.assertIn(self.partner1, self.product2.seller_ids.mapped("partner_id"))

    def test_04_multiple_products_pricelist_disabled(self):
        """Test multiple supplier pricelists not created when disabled"""
        self.env.company.purchase_pricelist_disable_autocreate = False

        seller_count_before_1 = len(self.product.seller_ids)
        seller_count_before_2 = len(self.product2.seller_ids)

        self.po_multi2.button_confirm()

        seller_count_after_1 = len(self.product.seller_ids)
        seller_count_after_2 = len(self.product2.seller_ids)

        self.assertEqual(seller_count_after_1, seller_count_before_1)
        self.assertEqual(seller_count_after_2, seller_count_before_2)
        self.assertNotIn(self.partner2, self.product.seller_ids.mapped("partner_id"))
        self.assertNotIn(self.partner2, self.product2.seller_ids.mapped("partner_id"))
