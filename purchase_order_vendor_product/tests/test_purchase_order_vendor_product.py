from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestPurchaseOrderVendorProduct(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_obj = cls.env["purchase.order"]
        cls.company_obj = cls.env["res.company"]
        # Partner
        cls.partner1 = cls.env.ref("base.res_partner_1")
        # Supplierinfo
        cls.product_supplierinfo_8 = cls.env.ref("product.product_supplierinfo_8")
        cls.product_supplierinfo_8.product_id = cls.env.ref(
            "product.product_product_11b"
        )

        product_supplierinfos = cls.env["product.supplierinfo"].search(
            [
                ("name", "=", cls.partner1.id),
                ("id", "!=", cls.product_supplierinfo_8.id),
            ]
        )
        product_supplierinfo_product_templates = [
            sup_info.product_tmpl_id for sup_info in product_supplierinfos
        ]

        cls.domain = [
            ("variant_seller_ids.name", "=?", cls.partner1.id),
            ("purchase_ok", "=", True),
            "|",
            ("company_id", "=", False),
            ("company_id", "=", cls.company_obj.id),
        ]

        cls.reference_product_list_ids = []
        for product_template in product_supplierinfo_product_templates:
            cls.reference_product_list_ids.extend(
                product_template.product_variant_ids.ids
            )
        cls.reference_product_list_ids.append(cls.product_supplierinfo_8.product_id.id)

    def test_name_search(self):
        product_list = self.env["product.product"].name_search(
            None, args=self.domain, operator="ilike"
        )
        product_list_ids = [product[0] for product in product_list]
        self.assertListEqual(
            sorted(self.reference_product_list_ids), sorted(product_list_ids)
        )
