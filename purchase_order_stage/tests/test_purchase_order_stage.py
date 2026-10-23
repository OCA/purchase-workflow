# Copyright 2025 Miguel Poyatos - Trey
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestPurchaseOrderStage(TransactionCase):
    def setUp(self):
        super().setUp()
        self.PurchaseOrderStage = self.env["purchase.order.stage"]
        self.PurchaseOrder = self.env["purchase.order"]

    def test_create_stage(self):
        stage = self.PurchaseOrderStage.create(
            {
                "name": "Test Stage",
                "sequence": 10,
                "active": True,
                "fold": False,
            }
        )
        self.assertEqual(stage.name, "Test Stage")
        self.assertTrue(stage.active)

    def test_create_purchase_order_with_stage(self):
        stage = self.PurchaseOrderStage.create(
            {
                "name": "Stage A",
            }
        )
        po = self.PurchaseOrder.create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "stage_id": stage.id,
            }
        )
        self.assertEqual(po.stage_id, stage)

    def test_update_stage_on_purchase_order(self):
        stage1 = self.PurchaseOrderStage.create(
            {
                "name": "Stage 1",
            }
        )
        stage2 = self.PurchaseOrderStage.create(
            {
                "name": "Stage 2",
            }
        )
        po = self.PurchaseOrder.create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "stage_id": stage1.id,
            }
        )
        po.stage_id = stage2.id
        self.assertEqual(po.stage_id, stage2)

    def test_stage_active_flag(self):
        stage = self.PurchaseOrderStage.create(
            {
                "name": "Inactive Stage",
                "active": False,
            }
        )
        self.assertFalse(stage.active)
