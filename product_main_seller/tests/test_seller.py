# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSeller(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Product = cls.env["product.product"]
        Partner = cls.env["res.partner"]

        cls.partner_woodcorner = Partner.create({"name": "Woodcorner"})
        cls.partner_azure = Partner.create({"name": "Azure Interior"})

        cls.product_workplace = Product.create(
            {"name": "Workplace", "default_code": "WORKPLACE"}
        )
        cls.product_acoustic = Product.create(
            {"name": "Acoustic Bloc Screens", "default_code": "ACOUSTIC"}
        )
        cls.product_with_var_chair = Product.create(
            {"name": "Chair (variant)", "default_code": "VAR_CHAIR"}
        )
        cls.product_without_seller_desk = Product.create(
            {"name": "Desk (no seller)", "default_code": "NOSELLERDESK"}
        )

        sellerInfo = cls.env["product.supplierinfo"]
        sellerInfo.create(
            {
                "partner_id": cls.partner_woodcorner.id,
                "product_tmpl_id": cls.product_acoustic.product_tmpl_id.id,
                "sequence": 1,
            }
        )
        for variant in cls.product_with_var_chair.product_tmpl_id.product_variant_ids:
            sellerInfo.create(
                {
                    "partner_id": cls.partner_woodcorner.id,
                    "product_id": variant.id,
                    "sequence": 1,
                }
            )
        sellerInfo.create(
            {
                "partner_id": cls.partner_woodcorner.id,
                "product_tmpl_id": cls.product_workplace.product_tmpl_id.id,
                "sequence": 1,
            }
        )

    def test_01_computed_main_vendor(self):
        self.assertEqual(
            self.product_acoustic.main_seller_id,
            self.product_acoustic.seller_ids[0].partner_id,
        )
        self.assertEqual(
            self.product_with_var_chair.main_seller_id,
            self.product_acoustic.product_variant_ids[0]
            .variant_seller_ids[0]
            .partner_id,
        )

    def test_02_replace_supplierinfo(self):
        self.product_acoustic.seller_ids = [
            Command.clear(),
            Command.create({"partner_id": self.partner_azure.id}),
        ]
        self.assertEqual(self.product_acoustic.main_seller_id.id, self.partner_azure.id)

    def test_03_add_supplierinfo_no_existing_supplierinfo(self):
        self.product_without_seller_desk.seller_ids = [
            Command.create({"partner_id": self.partner_azure.id}),
        ]
        self.assertEqual(
            self.product_without_seller_desk.main_seller_id.id, self.partner_azure.id
        )

    def test_03_add_supplierinfo_low_sequence(self):
        self.product_workplace.seller_ids.write({"sequence": 1})
        self.product_workplace.seller_ids = [
            Command.create({"sequence": 100, "partner_id": self.partner_azure.id}),
        ]
        self.assertNotEqual(
            self.product_workplace.main_seller_id.id, self.partner_azure.id
        )

    def test_03_add_supplierinfo_high_sequence(self):
        self.product_workplace.seller_ids.write({"sequence": 1000})
        self.product_workplace.seller_ids = [
            Command.create({"sequence": 100, "partner_id": self.partner_azure.id}),
        ]
        self.assertEqual(
            self.product_workplace.main_seller_id.id, self.partner_azure.id
        )

    def test_04_update_supplierinfo(self):
        self.product_acoustic.seller_ids.write({"partner_id": self.partner_azure.id})
        self.assertEqual(self.product_acoustic.main_seller_id.id, self.partner_azure.id)

    def test_05_unlink_supplierinfo(self):
        self.product_acoustic.seller_ids.unlink()
        self.assertEqual(self.product_acoustic.main_seller_id.id, False)
