from odoo import fields

from odoo.addons.stock.tests.test_report import TestReportsCommon


class TestReportForecast(TestReportsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.purchase_manual_delivery = True
        # Purchase Orders
        cls.po1 = cls.env["purchase.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_3").id,
            }
        )
        cls.po1_line1 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.po1.id,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "name": cls.product.name,
                "price_unit": cls.product.standard_price,
                "date_planned": fields.datetime.now(),
                "product_qty": 42.0,
            }
        )

    def test_report_forecast(self):
        """PO quantities without deliveries are mentioned on the forecast report"""
        self.po1.button_confirm()
        # Create delivery for a part of the ordered quantity
        wizard = (
            self.env["create.stock.picking.wizard"]
            .with_context(
                **{
                    "active_model": "purchase.order",
                    "active_id": self.po1.id,
                    "active_ids": self.po1.ids,
                }
            )
            .create({})
        )
        wizard.fill_lines(self.po1.order_line)
        # Transfer a quantity of 12
        wizard.line_ids.qty = 12
        wizard.create_stock_picking()
        picking = self.po1.picking_ids
        picking.move_line_ids.quantity = 12
        picking.button_validate()

        # Create an unvalidated picking with a quantity of 23
        wizard.line_ids.qty = 23
        wizard.create_stock_picking()

        # Checks the report.
        report_values, docs, lines = self.get_report_forecast(
            product_template_ids=self.product_template.ids
        )
        self.assertEqual(docs["no_delivery_purchase_qty"], 7)
        self.assertEqual(docs["qty"]["in"], 7)
        self.assertEqual(docs["quantity_on_hand"], 12)
        self.assertEqual(docs["virtual_available"], 35)
        self.assertEqual(
            docs["no_delivery_purchase_orders"],
            [{"id": self.po1.id, "name": self.po1.name}],
        )
