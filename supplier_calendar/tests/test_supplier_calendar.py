# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockWarehouseCalendar(TransactionCase):
    def setUp(self):
        super(TestStockWarehouseCalendar, self).setUp()
        self.move_obj = self.env["stock.move"]
        self.company = self.env.ref("base.main_company")
        self.company_partner = self.env.ref("base.main_partner")
        self.calendar = self.env.ref("resource.resource_calendar_std")
        self.supplier_info = self.env["product.supplierinfo"]
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseOrderLine = self.env["purchase.order.line"]
        self.stock_location = self.env["ir.model.data"].xmlid_to_object(
            "stock.stock_location_stock"
        )
        self.customer_location = self.env["ir.model.data"].xmlid_to_object(
            "stock.stock_location_customers"
        )
        self.picking_type_out = self.env["ir.model.data"].xmlid_to_object(
            "stock.picking_type_out"
        )
        self.route_buy = self.env.ref("purchase_stock.route_warehouse0_buy").id

        # Create product
        self.product = self.env["product.product"].create(
            {
                "name": "test product",
                "default_code": "PRD",
                "type": "product",
                "route_ids": [
                    (4, self.ref("stock.route_warehouse0_mto")),
                    (4, self.ref("purchase_stock.route_warehouse0_buy")),
                ],
            }
        )

        # Partner and Supplierinfo
        self.company_partner.write(
            {
                "delay_calendar_type": "supplier_calendar",
                "factory_calendar_id": self.calendar.id,
            }
        )
        self.seller_01 = self.supplier_info.create(
            {
                "name": self.company_partner.id,
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "delay": 3,
            }
        )

    def test_01_purchase_order_with_supplier_calendar(self):
        # Create a customer picking
        customer_picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.company_partner.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )

        customer_move = self.env["stock.move"].create(
            {
                "name": "move out",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 80.0,
                "procure_method": "make_to_order",
                "picking_id": customer_picking.id,
                "date_expected": "2097-01-14 09:00:00",  # Monday
            }
        )

        customer_move._action_confirm()

        purchase_order = self.env["purchase.order"].search(
            [("partner_id", "=", self.company_partner.id)]
        )
        self.assertTrue(purchase_order, "No purchase order created.")
        date_order = fields.Date.to_date(purchase_order.date_order)
        wednesday = fields.Date.to_date("2097-01-09 09:00:00")
        self.assertEqual(date_order, wednesday)  # Wednesday

    def test_02_purchase_order_supplier_calendar_global_leaves(self):
        # Global leaves
        self.calendar.write(
            {
                "global_leave_ids": [
                    (
                        0,
                        False,
                        {
                            "name": "Test",
                            "date_from": "2097-01-14",  # Monday
                            "date_to": "2097-01-19",  # Saturday
                        },
                    ),
                ],
            }
        )

        reference = "2097-01-14 09:00:00"  # Monday
        # With calendar
        result = self.company_partner.supplier_plan_days(reference, 3).date()
        next_wednesday = fields.Date.to_date("2097-01-23")
        self.assertEquals(result, next_wednesday)
        reference_2 = "2097-01-11 12:00:00"  # friday
        result = self.company_partner.supplier_plan_days(reference_2, 3).date()
        self.assertEquals(result, next_wednesday)
        # Without calendar
        self.company_partner.write(
            {"delay_calendar_type": "natural", "factory_calendar_id": False}
        )
        reference_3 = "2097-01-25 12:00:00"  # friday
        result = self.company_partner.supplier_plan_days(reference_3, 3).date()
        monday = fields.Date.to_date("2097-01-28")
        self.assertEquals(result, monday)
