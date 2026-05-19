# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from datetime import datetime

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestStockWarehouseCalendar(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.move_obj = cls.env["stock.move"]
        cls.company = cls.env.ref("base.main_company")
        cls.company_partner = cls.env.ref("base.main_partner")
        cls.calendar = cls.env.ref("resource.resource_calendar_std")
        cls.supplier_info = cls.env["product.supplierinfo"]
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.route_buy = cls.env.ref("purchase_stock.route_warehouse0_buy").id

        # Create product
        cls.product = cls.env["product.product"].create(
            {
                "name": "test product",
                "default_code": "PRD",
                "is_storable": True,
                "route_ids": [
                    Command.set(
                        [
                            cls.env.ref("stock.route_warehouse0_mto").id,
                            cls.env.ref("purchase_stock.route_warehouse0_buy").id,
                        ]
                    )
                ],
            }
        )

        # Partner and Supplierinfo
        cls.company_partner.write(
            {
                "delay_calendar_type": "supplier_calendar",
                "factory_calendar_id": cls.calendar.id,
            }
        )
        cls.seller_01 = cls.supplier_info.create(
            {
                "partner_id": cls.company_partner.id,
                "product_id": cls.product.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
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
                "description_picking": "move out",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 80.0,
                "procure_method": "make_to_order",
                "picking_id": customer_picking.id,
                "date": "2097-01-14 09:00:00",  # Monday
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
                    Command.create(
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
        self.assertEqual(result, next_wednesday)
        reference_2 = "2097-01-11 12:00:00"  # friday
        result = self.company_partner.supplier_plan_days(reference_2, 3).date()
        self.assertEqual(result, next_wednesday)
        # Without calendar
        self.company_partner.write(
            {"delay_calendar_type": "natural", "factory_calendar_id": False}
        )
        reference_3 = "2097-01-25 12:00:00"  # friday
        result = self.company_partner.supplier_plan_days(reference_3, 3).date()
        monday = fields.Date.to_date("2097-01-28")
        self.assertEqual(result, monday)

    def test_03_get_seller_date_planned_from_purchase_line(self):
        # We want to test the case when only the seller is provided and there is no
        # other date.
        test_date = self.company_partner.supplier_plan_days(
            datetime.today(), self.seller_01.delay
        )
        date = self.env["purchase.order.line"]._get_date_planned(self.seller_01)
        self.assertEqual(test_date, date)

    def test_04_supplier_plan_days_without_delay(self):
        date = fields.Date.to_date("2097-01-28")
        aux_date = self.company_partner.supplier_plan_days(date, 0).date()
        self.assertEqual(
            date, aux_date, "The date should be the same if the delay is 0."
        )
