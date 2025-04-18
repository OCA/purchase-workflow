# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSeller(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_workplace = cls.env.ref("product.product_product_24")
        cls.product_acoustic = cls.env.ref("product.product_product_25")
        cls.product_with_var_chair = cls.env.ref("product.product_product_11")
        cls.product_without_seller_desk = cls.env.ref("product.product_product_3")

        cls.partner_woodcorner = cls.env.ref("base.res_partner_1")
        cls.partner_azure = cls.env.ref("base.res_partner_12")

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
