# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestSubcontractedServiceProduct(TransactionCase):
    def setUp(self):
        super(TestSubcontractedServiceProduct, self).setUp()
        self.procurement_group_obj = self.env["procurement.group"]
        self.obj_warehouse = self.env["stock.warehouse"]

        # 1. find a supplier
        self.supplier = self.env.ref("base.res_partner_1")

        # 2. Create a product storable
        values = {
            "name": "Product that requires to purchase a service",
            "type": "product",
            "seller_ids": [
                (
                    0,
                    0,
                    {
                        "name": self.supplier.id,
                        "price": 100.0,
                    },
                )
            ],
        }
        self.product = self.env["product.product"].create(values)
        # 3. create a service subcontracted product
        values = {
            "name": "Service to attend",
            "type": "service",
            "seller_ids": [
                (
                    0,
                    0,
                    {
                        "name": self.supplier.id,
                        "price": 100.0,
                    },
                )
            ],
        }
        self.service = self.env["product.product"].create(values)
        # 4. create a test warehouse
        self.test_wh = self.obj_warehouse.create(
            {
                "name": "Test WH",
                "code": "T",
            }
        )
        # 5. find a customer
        self.customer = self.env["res.partner"].search(
            [("customer_rank", ">", 0)], limit=1
        )

    def test_01_subcontracted_service_procurement(self):
        """procure the storable product that requires a service and check
        a RFQ is created for the service"""
        values = {
            "warehouse_id": self.test_wh,
            "company_id": self.test_wh.company_id,
            "date_planned": fields.Date.today(),
            "group_id": self.test_wh.subcontracted_service_proc_rule_id.group_id,
        }
        self.product.subcontracted_product_id = self.service
        self.procurement_group_obj.run(
            [
                self.procurement_group_obj.Procurement(
                    self.product,
                    1,
                    self.product.uom_id,
                    self.test_wh.lot_stock_id,
                    "test",
                    "test",
                    self.test_wh.company_id,
                    values,
                ),
            ]
        )
        po_line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.service.id)], limit=1
        )
        self.assertEqual(len(po_line), 1)
        self.assertEqual(po_line.product_qty, 1)
        self.assertEqual(po_line.product_uom, self.service.uom_id)
        self.assertEqual(
            po_line.order_id.group_id,
            self.test_wh.subcontracted_service_proc_rule_id.group_id,
        )
        self.assertEqual(po_line.company_id, self.test_wh.company_id)
