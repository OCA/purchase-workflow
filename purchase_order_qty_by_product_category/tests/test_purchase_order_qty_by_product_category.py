# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestPurchaseOrderQtyByProductCategory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.uom_cubic_meter = cls.env.ref("uom.product_uom_cubic_meter")
        cls.uom_litre = cls.env.ref("uom.product_uom_litre")
        cls.partner = cls.env["res.partner"].create({"name": "Partner 1"})
        cls.category1, cls.category2 = cls.env["product.category"].create(
            [{"name": "Category 1"}, {"name": "Category 2"}]
        )
        cls.product1, cls.product2, cls.product3 = cls.env["product.product"].create(
            [
                {
                    "name": "Product 1",
                    "uom_id": cls.uom_unit.id,
                    "uom_po_id": cls.uom_unit.id,
                    "categ_id": cls.category1.id,
                },
                {
                    "name": "Product 2",
                    "uom_id": cls.uom_dozen.id,
                    "uom_po_id": cls.uom_dozen.id,
                    "categ_id": cls.category1.id,
                },
                {
                    "name": "Product 3",
                    "uom_id": cls.uom_cubic_meter.id,
                    "uom_po_id": cls.uom_cubic_meter.id,
                    "categ_id": cls.category2.id,
                },
            ]
        )
        cls.order_vals = {
            "partner_id": cls.partner.id,
            "company_id": cls.env.user.company_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product1.name,
                        "product_id": cls.product1.id,
                        "product_qty": 10.0,
                        "product_uom": cls.product1.uom_po_id.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": cls.product2.name,
                        "product_id": cls.product2.id,
                        "product_qty": 1.0,
                        "product_uom": cls.product2.uom_po_id.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": cls.product3.name,
                        "product_id": cls.product3.id,
                        "product_qty": 0.05,
                        "product_uom": cls.product3.uom_po_id.id,
                    },
                ),
            ],
        }

    def test_00_po_settings_from_param(self):
        # Case 1: both params inactive
        k, v = "purchase_ordered_qty_by_product_category.split_by_uom", "0"
        self.env["ir.config_parameter"].sudo().set_param(k, v)
        k, v = "purchase_ordered_qty_by_product_category.split_by_uom_reference", "0"
        self.env["ir.config_parameter"].sudo().set_param(k, v)
        po = self.env["purchase.order"].create(self.order_vals)
        self.assertFalse(po.category_qty_split_by_uom)
        self.assertFalse(po.category_qty_split_by_uom_reference)
        # Case 2: split by UoM active, split by reference UoM inactive
        k, v = "purchase_ordered_qty_by_product_category.split_by_uom", "1"
        self.env["ir.config_parameter"].sudo().set_param(k, v)
        po = self.env["purchase.order"].create(self.order_vals)
        self.assertTrue(po.category_qty_split_by_uom)
        self.assertFalse(po.category_qty_split_by_uom_reference)
        # Case 3: split by UoM active, split by reference UoM active
        k, v = "purchase_ordered_qty_by_product_category.split_by_uom_reference", "1"
        self.env["ir.config_parameter"].sudo().set_param(k, v)
        po = self.env["purchase.order"].create(self.order_vals)
        self.assertTrue(po.category_qty_split_by_uom)
        self.assertTrue(po.category_qty_split_by_uom_reference)
        # Case 4: split by UoM inactive, split by reference UoM active
        k, v = "purchase_ordered_qty_by_product_category.split_by_uom", "0"
        self.env["ir.config_parameter"].sudo().set_param(k, v)
        po = self.env["purchase.order"].create(self.order_vals)
        self.assertFalse(po.category_qty_split_by_uom)
        self.assertFalse(po.category_qty_split_by_uom_reference)

    def test_01_po_settings_from_settings(self):
        # Case 1: both params inactive
        with Form(
            self.env["res.config.settings"], "base.res_config_settings_view_form"
        ) as config_form:
            config_form.po_category_qty_split_by_uom_reference = False
            config_form.po_category_qty_split_by_uom = False
        config = config_form.save()
        config.execute()
        po = self.env["purchase.order"].create(self.order_vals)
        self.assertFalse(po.category_qty_split_by_uom)
        self.assertFalse(po.category_qty_split_by_uom_reference)
        # Case 2: split by UoM active, split by reference UoM inactive
        with Form(
            self.env["res.config.settings"], "base.res_config_settings_view_form"
        ) as config_form:
            config_form.po_category_qty_split_by_uom = True
        config = config_form.save()
        config.execute()
        po = self.env["purchase.order"].create(self.order_vals)
        self.assertTrue(po.category_qty_split_by_uom)
        self.assertFalse(po.category_qty_split_by_uom_reference)
        # Case 3: split by UoM active, split by reference UoM active
        with Form(
            self.env["res.config.settings"], "base.res_config_settings_view_form"
        ) as config_form:
            config_form.po_category_qty_split_by_uom_reference = True
        config = config_form.save()
        config.execute()
        po = self.env["purchase.order"].create(self.order_vals)
        self.assertTrue(po.category_qty_split_by_uom)
        self.assertTrue(po.category_qty_split_by_uom_reference)
        # Case 4: split by UoM inactive, split by reference UoM active
        with Form(
            self.env["res.config.settings"], "base.res_config_settings_view_form"
        ) as config_form:
            config_form.po_category_qty_split_by_uom = False
        config = config_form.save()
        config.execute()
        po = self.env["purchase.order"].create(self.order_vals)
        self.assertFalse(po.category_qty_split_by_uom)
        self.assertFalse(po.category_qty_split_by_uom_reference)

    def test_02_qty_splitting_by_category(self):
        po = self.env["purchase.order"].create(self.order_vals)
        self.assertEqual(len(po.qty_by_product_category_ids), 2)
        self.assertEqual(
            po.qty_by_product_category_ids.category_id, self.category1 + self.category2
        )
        rec1 = po.qty_by_product_category_ids.filtered(
            lambda r: r.category_id == self.category1
        )
        self.assertEqual(
            (
                rec1.qty_ordered,
                rec1.qty_received,
                rec1.qty_to_receive,
                rec1.qty_uom_id.id,
            ),
            (11, 0, 11, False),
        )
        rec2 = po.qty_by_product_category_ids.filtered(
            lambda r: r.category_id == self.category2
        )
        self.assertEqual(
            (
                rec2.qty_ordered,
                rec2.qty_received,
                rec2.qty_to_receive,
                rec2.qty_uom_id.id,
            ),
            (0.05, 0, 0.05, False),
        )

    def test_02_qty_splitting_by_category_and_uom(self):
        k, v = "purchase_ordered_qty_by_product_category.split_by_uom", "1"
        self.env["ir.config_parameter"].sudo().set_param(k, v)
        po = self.env["purchase.order"].create(self.order_vals)
        self.assertEqual(len(po.qty_by_product_category_ids), 3)
        self.assertEqual(
            po.qty_by_product_category_ids.category_id, self.category1 + self.category2
        )
        rec1 = po.qty_by_product_category_ids.filtered(
            lambda r: r.category_id == self.category1 and r.qty_uom_id == self.uom_unit
        )
        self.assertEqual(
            (
                rec1.qty_ordered,
                rec1.qty_received,
                rec1.qty_to_receive,
                rec1.qty_uom_id.id,
            ),
            (10, 0, 10, self.uom_unit.id),
        )
        rec2 = po.qty_by_product_category_ids.filtered(
            lambda r: r.category_id == self.category1 and r.qty_uom_id == self.uom_dozen
        )
        self.assertEqual(
            (
                rec2.qty_ordered,
                rec2.qty_received,
                rec2.qty_to_receive,
                rec2.qty_uom_id.id,
            ),
            (1, 0, 1, self.uom_dozen.id),
        )
        rec3 = po.qty_by_product_category_ids.filtered(
            lambda r: r.category_id == self.category2
            and r.qty_uom_id == self.uom_cubic_meter
        )
        self.assertEqual(
            (
                rec3.qty_ordered,
                rec3.qty_received,
                rec3.qty_to_receive,
                rec3.qty_uom_id.id,
            ),
            (0.05, 0, 0.05, self.uom_cubic_meter.id),
        )

    def test_03_qty_splitting_by_category_and_uom_reference(self):
        k, v = "purchase_ordered_qty_by_product_category.split_by_uom", "1"
        self.env["ir.config_parameter"].sudo().set_param(k, v)
        k, v = "purchase_ordered_qty_by_product_category.split_by_uom_reference", "1"
        self.env["ir.config_parameter"].sudo().set_param(k, v)
        po = self.env["purchase.order"].create(self.order_vals)
        self.assertEqual(len(po.qty_by_product_category_ids), 2)
        self.assertEqual(
            po.qty_by_product_category_ids.category_id, self.category1 + self.category2
        )
        rec1 = po.qty_by_product_category_ids.filtered(
            lambda r: r.category_id == self.category1 and r.qty_uom_id == self.uom_unit
        )
        self.assertEqual(
            (
                rec1.qty_ordered,
                rec1.qty_received,
                rec1.qty_to_receive,
                rec1.qty_uom_id.id,
            ),
            (22, 0, 22, self.uom_unit.id),
        )
        rec2 = po.qty_by_product_category_ids.filtered(
            lambda r: r.category_id == self.category2 and r.qty_uom_id == self.uom_litre
        )
        self.assertEqual(
            (
                rec2.qty_ordered,
                rec2.qty_received,
                rec2.qty_to_receive,
                rec2.qty_uom_id.id,
            ),
            (50, 0, 50, self.uom_litre.id),
        )
