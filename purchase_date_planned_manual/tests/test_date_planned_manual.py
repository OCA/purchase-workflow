# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.fields import first
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestDatePlannedManual(TransactionCase):
    def setUp(self):
        super().setUp()
        self.category = self.env["product.category"].create({"name": "Test category"})
        self.po_model = self.env["purchase.order"]
        self.pol_model = self.env["purchase.order.line"]
        self.pp_model = self.env["product.product"]
        # Create some partner, products and supplier info:
        self.route_buy_id = self.env.ref("purchase_stock.route_warehouse0_buy")
        self.rule = first(self.route_buy_id.rule_ids)
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test supplier",
                "supplier_rank": 1,
            }
        )

        self.warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.user.id)], limit=1
        )
        self.warehouse.delivery_steps = "pick_ship"
        self.final_location = self.partner.property_stock_customer

        self.product_1 = self._create_product(
            "Test product 1", self.category, self.partner
        )
        self.product_2 = self._create_product(
            "Test product 2", self.category, self.partner
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product_1, self.warehouse.lot_stock_id, 10.0
        )

        # Create purchase order and dates
        self.purchase_order = self.po_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.rule.picking_type_id.id,
            }
        )
        self.next_week_time = datetime.now() + timedelta(days=7)

    def _create_product(self, name, category, partner):
        product = self.env["product.product"].create(
            {
                "name": name,
                "type": "product",
                "categ_id": category.id,
                "seller_ids": [(0, 0, {"partner_id": partner.id, "min_qty": 1.0})],
            }
        )
        return product

    def test_manually_set_pol_date(self):
        """Tests the manual modification of scheduled date in purchase order
        lines."""
        last_week_time = datetime.now() - timedelta(days=7)

        po_line_1 = self.pol_model.create(
            {
                "order_id": self.purchase_order.id,
                "product_id": self.product_1.id,
                "date_planned": last_week_time,
                "name": "Test",
                "product_qty": 1.0,
                "product_uom": self.product_1.uom_id.id,
                "price_unit": 10.0,
            }
        )
        po_line_2 = self.pol_model.create(
            {
                "order_id": self.purchase_order.id,
                "product_id": self.product_2.id,
                "date_planned": self.next_week_time,
                "name": "Test",
                "product_qty": 10.0,
                "product_uom": self.product_2.uom_id.id,
                "price_unit": 20.0,
            }
        )
        self.assertTrue(
            po_line_1.date_planned < datetime.now(),
            "First test PO line should be predicted late.",
        )
        self.assertFalse(
            po_line_2.date_planned < datetime.now(),
            "Second test PO line should not be predicted late.",
        )
        self.purchase_order.button_confirm()
        self.assertEqual(
            po_line_1.date_planned,
            last_week_time,
            "Scheduled date should have benn respected.",
        )
        self.assertNotEqual(
            po_line_1.order_id.state, "draft", "state should not be draft'."
        )
        self.assertFalse(
            po_line_1.predicted_arrival_late,
            "predicted_arrival_late should be false when not in " "state 'draft'.",
        )
        with self.assertRaises(UserError):
            po_line_1.action_delayed_line()

    def _run_procurement(self, product, origin, values):
        procurement_group_obj = self.env["procurement.group"]
        procurement = procurement_group_obj.Procurement(
            product,
            1,
            product.uom_id,
            self.final_location,
            False,
            origin,
            self.warehouse.company_id,
            values,
        )
        rule = procurement_group_obj._get_rule(
            procurement.product_id, procurement.location_id, procurement.values
        )
        self.rule._run_buy([(procurement, rule)])

    def test_merging_of_po_lines_if_same_date_planned(self):
        """When only merge PO lines if they have same date_planned"""
        origin = "test_merging_of_po_lines_if_same_date_planned"
        values = {
            "warehouse_id": self.warehouse,
            "date_planned": self.next_week_time,
        }
        self._run_procurement(self.product_1, origin, values)
        orders = self.env["purchase.order"].search([("origin", "=", origin)])
        self.assertEqual(
            len(orders.order_line),
            1,
            "The PO should still have only one PO line.",
        )
        self.assertEqual(orders.order_line.product_qty, 1.0)
        # New procurement but 1 PO, 1 line, double qty.
        self._run_procurement(self.product_1, origin, values)
        orders = self.env["purchase.order"].search([("origin", "=", origin)])
        self.assertEqual(
            len(orders.order_line),
            1,
            "The PO should still have only one PO line.",
        )
        self.assertEqual(
            orders.order_line.product_qty,
            2.0,
            "The qty of the PO line should have increased by 1.",
        )
        self.assertEqual(
            orders.order_line.date_planned,
            self.next_week_time,
            "The date_planned of the PO line should be the same.",
        )

    def test_no_merging_of_po_lines_if_diff_date_planned(self):
        """No merge PO lines if they not have same date_planned"""
        origin = "test_no_merging_of_po_lines_if_diff_date_planned"
        values = {
            "warehouse_id": self.warehouse,
            "date_planned": self.next_week_time,
        }
        self._run_procurement(self.product_1, origin, values)
        orders = self.env["purchase.order"].search([("origin", "=", origin)])
        self.assertEqual(
            len(orders.order_line),
            1,
            "The PO should still have only one PO line.",
        )
        self.assertEqual(orders.order_line.product_qty, 1.0)
        self.assertEqual(orders.date_planned, self.next_week_time)
        # New procurement but 1 PO, 2 lines.
        values["date_planned"] += timedelta(days=1)
        self._run_procurement(self.product_1, origin, values)
        orders = self.env["purchase.order"].search([("origin", "=", origin)])
        self.assertEqual(len(orders), 1)
        self.assertEqual(
            len(orders.order_line),
            2,
            "A new PO line should have been create for the move.",
        )
        self.assertEqual(
            orders.order_line[0].date_planned,
            orders.date_planned,
            "The date_planned of the PO line should be the same.",
        )
        self.assertEqual(
            orders.order_line[1].date_planned,
            orders.date_planned + timedelta(days=1),
            "The date_planned of the PO line should be the same.",
        )
