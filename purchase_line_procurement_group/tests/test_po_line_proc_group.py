# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase


class TestPOLineProcurementGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        def _create_orderpoint(product, qty_min, qty_max, location):
            orderpoint_model = cls.env["stock.warehouse.orderpoint"]
            return orderpoint_model.create(
                {
                    "name": "OP/%s" % product.name,
                    "product_id": product.id,
                    "product_min_qty": qty_min,
                    "product_max_qty": qty_max,
                    "location_id": location.id,
                }
            )

        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        # Create supplier
        cls.pyromaniacs = cls.env["res.partner"].create(
            {"name": "Pyromaniacs Inc", "company_type": "company"}
        )
        cls.lighter = (
            cls.env["product.template"]
            .create(
                {
                    "name": "Lighter",
                    "type": "product",
                    "purchase_ok": True,
                    "seller_ids": [
                        (
                            0,
                            0,
                            {
                                "partner_id": cls.pyromaniacs.id,
                                "min_qty": 1,
                                "price": 1.0,
                            },
                        )
                    ],
                }
            )
            .product_variant_ids
        )

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"reception_steps": "three_steps"})
        wh2 = cls.env["stock.warehouse"].create(
            {"name": "WH2", "code": "WH2", "partner_id": False}
        )
        # Create WH > WH2 PG and route
        cls.wh_wh2_pg = cls.env["procurement.group"].create(
            {"name": "WH > WH2", "move_type": "direct"}
        )
        wh_wh2_route = cls.env["stock.route"].create(
            {
                "name": "WH > WH2",
                "product_selectable": True,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "WH>WH2",
                            "action": "pull",
                            "location_dest_id": wh2.lot_stock_id.id,
                            "location_src_id": cls.warehouse.lot_stock_id.id,
                            "procure_method": "make_to_order",
                            "picking_type_id": cls.env.ref(
                                "stock.picking_type_internal"
                            ).id,
                            "group_propagation_option": "fixed",
                            "group_id": cls.wh_wh2_pg.id,
                            "propagate_cancel": True,
                        },
                    )
                ],
            }
        )
        cls.lighter.write({"route_ids": [(4, wh_wh2_route.id)]})
        _create_orderpoint(cls.lighter, 15, 30, cls.warehouse.lot_stock_id)
        _create_orderpoint(cls.lighter, 10, 20, wh2.lot_stock_id)

        # Force parent store computation after creation of WH2 because location
        # quantities are computed using parent_left _right in domain
        cls.env["stock.location"]._parent_store_compute()

    def test_po_line_find_candidate_with_group(self):
        """Ensure that our `_find_candidate` override gives a right match when
        comparing the procurement group"""

        def create_po_line_in_new_po(product, qty, group=False):
            """Shortcut to create a draft purchase of a `product`. A new
            purchase order is created with a single line."""
            po = self.env["purchase.order"].create(
                {
                    "partner_id": self.pyromaniacs.id,
                    "group_id": group and group.id or False,
                }
            )
            po_line = self.env["purchase.order.line"].create(
                {
                    "order_id": po.id,
                    "product_id": product.id,
                    "product_qty": qty,
                    "product_uom": product.uom_id.id,
                    "price_unit": 1.0,
                    "procurement_group_id": group and group.id or False,
                }
            )
            return po_line

        def find_candidate(po_lines, values):
            """Shortcut to call `_find_candidate` with pre-filled values"""
            return po_lines._find_candidate(
                product_id=self.lighter,
                product_qty=1.0,
                product_uom=self.lighter.uom_id.id,
                location_id=self.stock_location,
                name="",
                origin="",
                company_id=self.env.company.id,
                values=values,
            )

        # Procurement group that will be used as a filter
        my_group = self.env["procurement.group"].create(
            {"name": "Group", "move_type": "direct"}
        )

        # Create a first purchase for our lighter without procurement group
        po1_line = create_po_line_in_new_po(self.lighter, 1.0, False)

        # Create a second purchase for our lighter with a dedicated
        # procurement group
        po2_line = create_po_line_in_new_po(self.lighter, 1.0, my_group)

        # Create a pool of purchase order lines
        po_lines = po1_line + po2_line

        # Check match when no procurement group is given
        match_lines_1 = find_candidate(
            po_lines,
            values={
                "orderpoint_id": False,
                "propagate_cancel": True,
            },
        )
        self.assertEqual(len(match_lines_1), 1)
        self.assertEqual(match_lines_1.id, po1_line.id)

        # Check match when an empty procurement group is given
        match_lines_2 = find_candidate(
            po_lines,
            values={
                "orderpoint_id": False,
                "propagate_cancel": True,
                "group_id": False,
            },
        )
        self.assertEqual(len(match_lines_2), 1)
        self.assertEqual(match_lines_2.id, po1_line.id)

        # Check match when a specific procurement group is given
        match_lines_3 = find_candidate(
            po_lines,
            values={
                "orderpoint_id": False,
                "propagate_cancel": True,
                "group_id": my_group,
            },
        )
        self.assertEqual(len(match_lines_3), 1)
        self.assertEqual(match_lines_3.id, po2_line.id)

    def test_po_line_proc_group(self):
        # Ensure PO lines generated by the scheduler have proper PG
        self.env["procurement.group"].run_scheduler()
        po = self.env["purchase.order"].search(
            [("partner_id", "=", self.pyromaniacs.id)]
        )
        self.assertEqual(len(po.order_line), 2)
        for line in po.order_line:
            self.assertEqual(line.product_id, self.lighter)
            if line.procurement_group_id == self.wh_wh2_pg:
                self.assertAlmostEqual(line.product_qty, 20)
            else:
                self.assertAlmostEqual(line.product_qty, 30)
        # Ensure stock moves generated by PO confirmation have proper PG
        po.button_confirm()
        input_moves = self.env["stock.move"].search(
            [
                ("product_id", "=", self.lighter.id),
                ("location_dest_id", "=", self.warehouse.wh_input_stock_loc_id.id),
            ]
        )
        self.assertEqual(len(input_moves), 2)
        for move in input_moves:
            self.assertEqual(move.product_id, self.lighter)
            if move.group_id == self.wh_wh2_pg:
                self.assertAlmostEqual(move.product_uom_qty, 20.0)
            else:
                self.assertAlmostEqual(move.product_uom_qty, 30.0)
