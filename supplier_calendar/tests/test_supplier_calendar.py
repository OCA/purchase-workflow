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

    def test_05_company_default_supplier_calendar(self):
        reference = "2097-01-11 12:00:00"  # friday
        # Without default calendar, it counts natural days
        self.company_partner.write(
            {"delay_calendar_type": "company_calendar", "factory_calendar_id": False}
        )
        result = self.company_partner.supplier_plan_days(
            reference, 3, self.company
        ).date()
        self.assertEqual(result, fields.Date.to_date("2097-01-14"))  # Monday
        self.company_partner.delay_calendar_type = "natural"
        self.company.supplier_calendar_id = self.calendar
        # Natural days stay natural days
        result = self.company_partner.supplier_plan_days(
            reference, 3, self.company
        ).date()
        self.assertEqual(result, fields.Date.to_date("2097-01-14"))  # Monday
        self.company_partner.delay_calendar_type = "company_calendar"
        result = self.company_partner.supplier_plan_days(
            reference, 3, self.company
        ).date()
        self.assertEqual(result, fields.Date.to_date("2097-01-16"))  # Wednesday
        # A line without vendor keeps the core date
        self.assertTrue(
            self.PurchaseOrderLine._get_date_planned(self.env["product.supplierinfo"])
        )

    def test_06_delay_calendar_type_default(self):
        partner = self.env["res.partner"].create({"name": "Vendor"})
        self.assertEqual(partner.delay_calendar_type, "natural")
        self.company.supplier_calendar_id = self.calendar
        partner = self.env["res.partner"].create({"name": "Vendor"})
        self.assertEqual(partner.delay_calendar_type, "company_calendar")

    def test_07_settings_warn_vendors_in_natural_days(self):
        self.company_partner.write(
            {
                "supplier_rank": 1,
                "delay_calendar_type": "natural",
                "factory_calendar_id": False,
            }
        )
        settings = self.env["res.config.settings"].create(
            {"supplier_calendar_id": self.calendar.id}
        )
        self.assertTrue(settings.supplier_calendar_natural_count)
        settings.action_set_vendors_default_supplier_calendar()
        self.assertEqual(self.company_partner.delay_calendar_type, "company_calendar")
        settings.invalidate_recordset()
        self.assertFalse(settings.supplier_calendar_natural_count)

    def test_08_settings_button_only_changes_the_configured_company(self):
        company_b = self.env["res.company"].create({"name": "Company B"})
        vendor_b = self.env["res.partner"].create(
            {
                "name": "Vendor of company B",
                "company_id": company_b.id,
                "supplier_rank": 1,
                "delay_calendar_type": "natural",
            }
        )
        shared_vendor = self.env["res.partner"].create(
            {
                "name": "Shared vendor",
                "supplier_rank": 1,
                "delay_calendar_type": "natural",
            }
        )
        settings = (
            self.env["res.config.settings"]
            .with_context(allowed_company_ids=[self.company.id, company_b.id])
            .create({"supplier_calendar_id": self.calendar.id})
        )
        self.assertEqual(settings.company_id, self.company)
        settings.action_set_vendors_default_supplier_calendar()
        self.assertEqual(shared_vendor.delay_calendar_type, "company_calendar")
        self.assertEqual(vendor_b.delay_calendar_type, "natural")
