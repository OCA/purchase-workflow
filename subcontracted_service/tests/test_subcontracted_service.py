# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# Copyright 2017-23 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestSubcontractedService(TransactionCase):
    def _get_common_procurement_values(self):
        return {
            "warehouse_id": self.test_wh,
            "company_id": self.test_wh.company_id,
            "date_planned": fields.Date.today(),
            "group_id": self.test_wh.subcontracting_service_proc_rule_id.group_id,
        }

    def _run_common_procurement(self, product, qty, values):
        self.procurement_group_obj.run(
            [
                self.procurement_group_obj.Procurement(
                    product,
                    qty,
                    product.uom_id,
                    self.test_wh.lot_stock_id,
                    "test",
                    "test",
                    self.test_wh.company_id,
                    values,
                ),
            ]
        )

    def _assert_procurement_purchase_line(self, po_line, product, qty):
        self.assertEqual(len(po_line), 1)
        self.assertEqual(po_line.product_qty, qty)
        self.assertEqual(po_line.product_uom, product.uom_id)
        self.assertEqual(
            po_line.order_id.group_id,
            self.test_wh.subcontracting_service_proc_rule_id.group_id,
        )
        self.assertEqual(po_line.company_id, self.test_wh.company_id)

    def setUp(self):
        super().setUp()
        self.procurement_group_obj = self.env["procurement.group"]
        self.obj_warehouse = self.env["stock.warehouse"]

        # 1. find a supplier
        self.supplier = self.env.ref("base.res_partner_1")

        # 2. create a service product unconfigured
        values = {
            "name": "Service Subcontracted",
            "type": "service",
            "seller_ids": [
                (
                    0,
                    0,
                    {
                        "partner_id": self.supplier.id,
                        "price": 100.0,
                    },
                )
            ],
        }
        self.pdt_service = self.env["product.product"].create(values)
        # 3. create a test warehouse
        self.test_wh = self.obj_warehouse.create(
            {
                "name": "Test WH",
                "code": "T",
            }
        )
        # 4. find a customer
        self.customer = self.env["res.partner"].search(
            [("customer_rank", ">", 0)], limit=1
        )

    def test_01_wh_stock_rule(self):
        """Tests if the procurement rule for subcontracting services is
        assigned properly to the warehouse."""
        wh = self.test_wh
        self.assertNotEqual(
            wh.subcontracting_service_proc_rule_id,
            False,
            "Subcontracting Service Rule not assigned to the " "Warehouse.",
        )
        picking_wh = wh.subcontracting_service_proc_rule_id.picking_type_id.warehouse_id
        self.assertEqual(picking_wh, wh, "Rule wrongly configured.")

    def test_02_subcontracted_service_procurement(self):
        """Test if the subcontracting service procurement rule is correctly
        assigned when creating a procurement for a subcontracted service
        product."""
        self.assertTrue(self.pdt_service.purchase_ok, "Product must be purchasable.")
        self.pdt_service.property_subcontracted_service = True
        values = self._get_common_procurement_values()
        self._run_common_procurement(self.pdt_service, 1, values)
        po_line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.pdt_service.id)], limit=1
        )
        self._assert_procurement_purchase_line(po_line, self.pdt_service, 1)

    def test_03_subcontracted_service_procurement_no_routes(self):
        """Test if the subcontracting service procurement rule is correctly
        assigned when creating a procurement for a subcontracted service
        product without routes."""
        self.assertTrue(self.pdt_service.purchase_ok, "Product must be purchasable.")
        self.pdt_service.property_subcontracted_service = True
        self.pdt_service.route_ids = False
        values = self._get_common_procurement_values()
        self._run_common_procurement(self.pdt_service, 1, values)
        po_line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.pdt_service.id)], limit=1
        )
        self._assert_procurement_purchase_line(po_line, self.pdt_service, 1)

    def test_04_subcontracted_service_purchase_not_ok(self):
        """Test that no procurement is created when the product is not
        purchasable even if it is a subcontracted service."""
        self.pdt_service.property_subcontracted_service = True
        self.pdt_service.purchase_ok = False
        values = self._get_common_procurement_values()
        self._run_common_procurement(self.pdt_service, 1, values)
        po_line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.pdt_service.id)], limit=1
        )
        self.assertEqual(len(po_line), 0)
