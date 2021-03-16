# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestPurchaseLot(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        large_cabinet = cls.env.ref("product.product_product_6")
        cls.large_cabinet = large_cabinet.copy()
        buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        mto_route = cls.env.ref("stock.route_warehouse0_mto")
        mto_route.write({"active": True})
        # ensure full make to order and not mts or mto
        mto_route.rule_ids.write({"procure_method": "make_to_order"})
        cls.large_cabinet.write(
            {
                "route_ids": [(4, buy_route.id, 0), (4, mto_route.id, 0)],
                "tracking": "lot",
            }
        )
        cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.large_cabinet.product_tmpl_id.id,
                "product_id": cls.large_cabinet.id,
                "name": cls.env.ref("base.res_partner_1").id,
            }
        )
        cls.out_picking_type = cls.env.ref("stock.picking_type_out")

    def test_purchase_lot(self):
        lot1 = self.env["stock.production.lot"].create(
            {
                "name": "lot1",
                "product_id": self.large_cabinet.id,
                "company_id": self.warehouse.company_id.id,
            }
        )
        lot2 = self.env["stock.production.lot"].create(
            {
                "name": "lot2",
                "product_id": self.large_cabinet.id,
                "company_id": self.warehouse.company_id.id,
            }
        )

        group = self.env["procurement.group"].create({"name": "My test delivery"})
        vals_list = [
            {
                "product_id": self.large_cabinet.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.customer_loc.id,
                "product_uom_qty": 1,
                "product_uom": self.large_cabinet.uom_id.id,
                "name": "test",
                "procure_method": "make_to_order",
                "warehouse_id": self.warehouse.id,
                "restrict_lot_id": lot1.id,
                "picking_type_id": self.out_picking_type.id,
                "group_id": group.id,
            },
            {
                "product_id": self.large_cabinet.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.customer_loc.id,
                "product_uom_qty": 1,
                "product_uom": self.large_cabinet.uom_id.id,
                "name": "test",
                "procure_method": "make_to_order",
                "warehouse_id": self.warehouse.id,
                "restrict_lot_id": lot2.id,
                "picking_type_id": self.out_picking_type.id,
                "group_id": group.id,
            },
        ]
        moves = self.env["stock.move"].create(vals_list)
        moves._action_confirm()
        pols = self.env["purchase.order.line"].search(
            [("move_dest_ids", "in", moves.ids)]
        )
        # not merged because of different lot
        self.assertEqual(len(pols), 2)
        pol1 = pols.filtered(lambda l: l.move_dest_ids.restrict_lot_id.id == lot1.id)
        self.assertEqual(pol1.lot_id.id, lot1.id)
        pol1.order_id.button_confirm()
        self.assertEqual(pol1.move_ids.restrict_lot_id.id, lot1.id)
