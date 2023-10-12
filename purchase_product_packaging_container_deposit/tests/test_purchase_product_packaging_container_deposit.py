# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form

from odoo.addons.product_packaging_container_deposit.tests.common import Common


class TestPurchaseProductPackagingContainerDeposit(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "company_id": cls.env.company.id,
                "partner_id": cls.env.ref("base.res_partner_12").id,
            }
        )
        # Assign default purchase price
        cls.package_type_pallet.container_deposit_product_id.standard_price = 8069
        cls.package_type_box.container_deposit_product_id.standard_price = 8069
        cls.product_a.standard_price = 8080
        cls.product_c.standard_price = 8080

    def test_confirmed_purchase_product_packaging_container_deposit_quantities(self):
        """Container deposit is added on confirmed orders"""
        self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "name": self.product_a.name,
                "product_id": self.product_a.id,
                "product_qty": 50,
            }
        )
        self.purchase_order.button_confirm()
        deposit_lines = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id
            in self.product_a.mapped(
                "packaging_ids.package_type_id.container_deposit_product_id"
            )
        )
        self.assertEqual(len(deposit_lines), 1)

    def test_purchase_product_packaging_container_deposit_quantities_case1(self):
        """
        Case 1: Product A | qty = 280. Result:
                280 // 240 = 1 => add SO line for 1 Pallet
                280 // 24 (biggest PACK) => add SO line for 11 boxes of 24
        """
        self.env["purchase.order.line"].create(
            [
                {
                    "order_id": self.purchase_order.id,
                    "name": self.product_a.name,
                    "product_id": self.product_a.id,
                    "product_qty": 280,
                },
                {
                    "order_id": self.purchase_order.id,
                    "name": self.product_c.name,
                    "product_id": self.product_c.id,
                    "product_qty": 1,
                },
            ]
        )

        pallet_line = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id == self.pallet
        )
        box_line = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(pallet_line.product_qty, 1)
        self.assertEqual(box_line.product_qty, 11)

    def test_purchase_product_packaging_container_deposit_quantities_case2(self):
        """
        Case 2: Product A | qty = 280 and packaging=Box of 12. Result:
            280 // 240 = 1 => add SO line for 1 Pallet
            280 // 12 (forced packaging for Boxes) => add SO line for 23 boxes of 12
        """
        self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "name": self.product_a.name,
                "product_id": self.product_a.id,
                "product_qty": 280,
                # Box of 12
                "product_packaging_id": self.packaging[0].id,
            },
        )
        # Filter lines with boxes
        box_lines = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(box_lines[0].product_qty, 23)

    def test_purchase_product_packaging_container_deposit_quantities_case3(self):
        """
        Case 3: Product A & Product B. Both have a deposit of 1 box of 24. Result:
                Only one line for 2 boxes of 24
        """
        self.env["purchase.order.line"].create(
            [
                {
                    "order_id": self.purchase_order.id,
                    "name": self.product_a.name,
                    "product_id": self.product_a.id,
                    "product_qty": 24,
                },
                {
                    "order_id": self.purchase_order.id,
                    "name": self.product_b.name,
                    "product_id": self.product_b.id,
                    "product_qty": 24,
                },
            ]
        )
        box_lines = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(box_lines[0].product_qty, 2)

    def test_purchase_product_packaging_container_deposit_quantities_case4(self):
        """
        Case 4: Product A | qty = 24. Result:
                24 // 24 (biggest PACK) => add SO line for 1 box of 24
                Product A | Increase to 48. Result:
                48 // 24 (biggest PACK) =>  recompute previous SO line with 2 boxes of 24
                Add manually Product A container deposit (Box). Result:
                1 SO line with 2 boxes of 24 (System added)
                + 1 SO line with 1 box (manually added)
        """
        order_line = self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "name": self.product_a.name,
                "product_id": self.product_a.id,
                "product_qty": 24,
            },
        )
        order_line.write({"product_qty": 48})
        deposit_line = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id
            in self.product_a.mapped(
                "packaging_ids.package_type_id.container_deposit_product_id"
            )
        )
        self.assertEqual(deposit_line.name, "Box")
        self.assertEqual(deposit_line.product_qty, 2.0)

        # Add manually 1 box
        self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "name": self.package_type_box.container_deposit_product_id.name,
                "product_id": self.package_type_box.container_deposit_product_id.id,
                "product_qty": 1,
            }
        )

        box_lines = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(box_lines[0].product_qty, 2)
        self.assertEqual(box_lines[1].product_qty, 1)

    def test_purchase_product_packaging_container_deposit_quantities_case5(self):
        """
        Case 5: Product A | qty = 280 on confirmed order.
                Product A | Increase qty to 480. Result:
                480 // 240 = 1 => add SO line for 2 Pallet
                480 // 24 (biggest PACK) => add SO line for 20 boxes of 24
        """
        self.env["purchase.order.line"].create(
            [
                {
                    "order_id": self.purchase_order.id,
                    "name": self.product_a.name,
                    "product_id": self.product_a.id,
                    "product_qty": 280,
                },
                {
                    "order_id": self.purchase_order.id,
                    "name": self.product_c.name,
                    "product_id": self.product_c.id,
                    "product_qty": 1,
                },
            ]
        )
        self.purchase_order.button_confirm()
        self.purchase_order.order_line[0].product_qty = 480

        # Odoo standard try to propose a suitable product packaging.
        # We don't want it in that case
        self.purchase_order.order_line[0].product_packaging_id = False

        pallet_line = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id == self.pallet
        )
        box_line = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(pallet_line.product_qty, 2)
        self.assertEqual(box_line.product_qty, 20)

    def test_purchase_product_packaging_container_deposit_quantities_case6(self):
        """
        Case 6: Product A | qty = 280 on confirmed order.
                Product A | qty_received = 280. Result:
                Received 1 Pallet
                Received 11 Boxes

        """
        self.env["purchase.order.line"].create(
            [
                {
                    "order_id": self.purchase_order.id,
                    "name": self.product_a.name,
                    "product_id": self.product_a.id,
                    "product_qty": 280,
                },
            ]
        )
        self.purchase_order.button_confirm()

        pick = self.purchase_order.picking_ids
        pick.move_ids.write({"quantity_done": 280})
        pick.button_validate()

        pallet_line = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id == self.pallet
        )
        box_line = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(pallet_line.qty_received, 1)
        self.assertEqual(box_line.qty_received, 11)

    def test_purchase_product_packaging_container_deposit_quantities_case7(self):
        """
        Case 7.1: Product A | qty = 280 on confirmed order.
                Product A | Partial shipment (qty_received = 140). Result:
                Received 140 // 280 = 0 Pallet
                Received 140 // 24 = 5 Boxes
        Case 7.2: Product A | Increase received quantity (qty_received = 200). Result:

                Received 200 // 280 = 0 Pallet
                Received 200 // 24 = 5 Boxes
        """
        self.env["purchase.order.line"].create(
            [
                {
                    "order_id": self.purchase_order.id,
                    "name": self.product_a.name,
                    "product_id": self.product_a.id,
                    "product_qty": 280,
                },
            ]
        )
        self.purchase_order.button_confirm()

        pick = self.purchase_order.picking_ids
        pick.move_ids.write({"quantity_done": 140})
        wiz_act = pick.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(**wiz_act["context"])
        ).save()
        wiz.process()

        pallet_line = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id == self.pallet
        )
        box_line = self.purchase_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )

        (pallet_line | box_line).invalidate_cache()
        self.assertEqual(pallet_line.qty_received, 0)
        self.assertEqual(box_line.qty_received, 5)

        self.purchase_order.order_line[0].qty_received = 200
        self.assertEqual(pallet_line.qty_received, 0)
        self.assertEqual(box_line.qty_received, 8)

    def test_sale_product_packaging_container_deposit_quantities_case8(self):
        """Test add and delete container deposit lines"""
        purchase_form = Form(self.env["purchase.order"])
        purchase_form.partner_id = self.purchase_order.partner_id
        with purchase_form.order_line.new() as line:
            line.product_id = self.product_a
            line.product_qty = 280
        purchase = purchase_form.save()
        with purchase_form.order_line.edit(0) as line:
            line.product_qty = 10

        lines_to_delete = purchase.order_line.filtered(
            lambda ol: ol.product_id == self.pallet or ol.product_id == self.box
        )
        with self._check_delete_after_commit(lines_to_delete):
            purchase_form.save()
