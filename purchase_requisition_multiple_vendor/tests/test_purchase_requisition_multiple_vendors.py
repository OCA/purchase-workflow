# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tests.common import tagged

from odoo.addons.purchase_requisition.tests.common import TestPurchaseRequisitionCommon


@tagged("post_install", "-at_install")
class TestPurchaseRequisitionMultipleVendors(TestPurchaseRequisitionCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.alternative_vendor_1 = cls.env["res.partner"].create(
            {"name": "Alternative Vendor-1"}
        )
        cls.alternative_vendor_2 = cls.env["res.partner"].create(
            {"name": "Alternative Vendor-2"}
        )

    def create_purchase(self):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.res_partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_09.id,
                            "name": "Product",
                            "product_qty": 5.0,
                            "product_uom": self.env.ref("uom.product_uom_dozen").id,
                            "price_unit": 50.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Products",
                            "display_type": "line_section",
                            "product_qty": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Products",
                            "display_type": "line_section",
                            "product_qty": 0.0,
                        },
                    ),
                ],
            }
        )

    def create_requisition_wizard(self, orig_po, copy=True):
        action = orig_po.action_create_alternative()
        alt_po_wiz = Form(
            self.env["purchase.requisition.create.alternative"].with_context(
                **action["context"]
            )
        )
        alt_po_wiz.partner_ids = self.alternative_vendor_1 + self.alternative_vendor_2
        alt_po_wiz.copy_products = copy
        alt_po_wiz = alt_po_wiz.save()
        return alt_po_wiz

    def test_requisition_multiple_vendors_single(self):
        orig_po = self.create_purchase()
        action = orig_po.action_create_alternative()
        alt_po_wiz = Form(
            self.env["purchase.requisition.create.alternative"].with_context(
                **action["context"]
            )
        )
        alt_po_wiz.partner_ids = self.alternative_vendor_1
        self.assertEqual(alt_po_wiz.partner_id, self.alternative_vendor_1)
        alt_po_wiz = alt_po_wiz.save()
        alt_po_wiz.action_create_alternative()
        self.assertEqual(len(orig_po.alternative_po_ids), 2)
        alt_po = orig_po.alternative_po_ids.filtered(
            lambda po: po.partner_id == self.alternative_vendor_1
        )
        self.assertTrue(alt_po)
        self.assertEqual(len(alt_po.alternative_po_ids), 2)

    def test_requisition_multiple_vendors_copy_lines(self):
        orig_po = self.create_purchase()
        alt_po_wiz = self.create_requisition_wizard(orig_po)
        alt_po_wiz.action_create_alternative()
        self.assertEqual(len(orig_po.alternative_po_ids), 3)

        alt_po_1 = orig_po.alternative_po_ids.filtered(
            lambda po: po.partner_id == self.alternative_vendor_1
        )
        self.assertTrue(alt_po_1)
        self.assertEqual(len(alt_po_1.order_line), 3)
        self.assertEqual(
            orig_po.order_line[0].product_id, alt_po_1.order_line[0].product_id
        )
        self.assertEqual(
            orig_po.order_line[0].product_qty, alt_po_1.order_line[0].product_qty
        )
        self.assertEqual(
            orig_po.order_line[0].product_uom, alt_po_1.order_line[0].product_uom
        )
        self.assertEqual(
            (orig_po.order_line[1].display_type, orig_po.order_line[1].name),
            (alt_po_1.order_line[1].display_type, alt_po_1.order_line[1].name),
        )
        self.assertEqual(
            (orig_po.order_line[2].display_type, orig_po.order_line[2].name),
            (alt_po_1.order_line[2].display_type, alt_po_1.order_line[2].name),
        )
        self.assertEqual(len(alt_po_1.alternative_po_ids), 3)

        alt_po_2 = orig_po.alternative_po_ids.filtered(
            lambda po: po.partner_id == self.alternative_vendor_2
        )
        self.assertTrue(alt_po_2)
        self.assertEqual(len(alt_po_2.order_line), 3)
        self.assertEqual(
            orig_po.order_line[0].product_id, alt_po_2.order_line[0].product_id
        )
        self.assertEqual(
            orig_po.order_line[0].product_qty, alt_po_2.order_line[0].product_qty
        )
        self.assertEqual(
            orig_po.order_line[0].product_uom, alt_po_2.order_line[0].product_uom
        )
        self.assertEqual(
            (orig_po.order_line[1].display_type, orig_po.order_line[1].name),
            (alt_po_2.order_line[1].display_type, alt_po_2.order_line[1].name),
        )
        self.assertEqual(
            (orig_po.order_line[2].display_type, orig_po.order_line[2].name),
            (alt_po_2.order_line[2].display_type, alt_po_2.order_line[2].name),
        )
        self.assertEqual(len(alt_po_2.alternative_po_ids), 3)

    def test_requisition_multiple_vendors_no_copy_lines(self):
        orig_po = self.env["purchase.order"].create(
            {
                "partner_id": self.res_partner_1.id,
            }
        )
        alt_po_wiz = self.create_requisition_wizard(orig_po, False)
        alt_po_wiz.action_create_alternative()
        self.assertEqual(len(orig_po.alternative_po_ids), 3)

        alt_po_1 = orig_po.alternative_po_ids.filtered(
            lambda po: po.partner_id == self.alternative_vendor_1
        )
        self.assertTrue(alt_po_1)
        self.assertEqual(len(alt_po_1.order_line), 0)

        alt_po_2 = orig_po.alternative_po_ids.filtered(
            lambda po: po.partner_id == self.alternative_vendor_2
        )
        self.assertTrue(alt_po_2)
        self.assertEqual(len(alt_po_2.order_line), 0)

    def test_requisition_multiple_vendors_second_flow(self):
        orig_po = self.create_purchase()
        # First Flow
        alt_po_wiz = self.create_requisition_wizard(orig_po)
        alt_po_wiz.action_create_alternative()
        # Second Flow
        alt_po_wiz = self.create_requisition_wizard(orig_po)
        alt_po_wiz.action_create_alternative()

        self.assertEqual(len(orig_po.alternative_po_ids), 5)

        alt_po_1 = orig_po.alternative_po_ids.filtered(
            lambda po: po.partner_id == self.alternative_vendor_1
        )
        self.assertEqual(len(alt_po_1), 2)
        self.assertEqual(len(alt_po_1[0].alternative_po_ids), 5)
        self.assertEqual(len(alt_po_1[1].alternative_po_ids), 5)

        alt_po_2 = orig_po.alternative_po_ids.filtered(
            lambda po: po.partner_id == self.alternative_vendor_2
        )
        self.assertEqual(len(alt_po_2), 2)
        self.assertEqual(len(alt_po_2[0].alternative_po_ids), 5)
        self.assertEqual(len(alt_po_2[1].alternative_po_ids), 5)

    def test_requisition_multiple_vendors_creation_block(self):
        orig_po = self.create_purchase()
        self.alternative_vendor_2.write(
            {"purchase_warn": "block", "purchase_warn_msg": "block message"}
        )
        self.env.ref("purchase.group_warning_purchase").write(
            {"users": [Command.link(self.env.user.id)]}
        )
        alt_po_wiz = self.create_requisition_wizard(orig_po)
        self.assertTrue(alt_po_wiz.creation_blocked)
        self.assertTrue(alt_po_wiz.purchase_warn_msg)
        self.assertTrue(self.alternative_vendor_2.name in alt_po_wiz.purchase_warn_msg)
        with self.assertRaises(UserError):
            alt_po_wiz.action_create_alternative()
