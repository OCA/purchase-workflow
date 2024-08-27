# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.tests import Form

from odoo.tools import mute_logger


class TestPurchaseLot(TransactionCase):
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
                "partner_id": cls.env.ref("base.res_partner_1").id,
            }
        )
        cls.out_picking_type = cls.env.ref("stock.picking_type_out")
        cls.supplier = cls.env["res.partner"].create({"name": "Vendor"})
        cls.customer = cls.env["res.partner"].create({"name": "Customer"})
        cls.external_serial_product = cls.env["product.product"].create(
            {
                "name": "Pen drive",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_1").id,
                "lst_price": 100.0,
                "standard_price": 0.0,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "seller_ids": [
                    (0, 0, {"delay": 1, "partner_id": cls.supplier.id, "min_qty": 2.0})
                ],
                "route_ids": [(4, buy_route.id, 0), (4, mto_route.id, 0)],
            }
        )
        cls.external_serial_product.product_tmpl_id.tracking = "serial"

    def test_purchase_lot(self):
        lot1 = self.env["stock.lot"].create(
            {
                "name": "lot1",
                "product_id": self.large_cabinet.id,
                "company_id": self.warehouse.company_id.id,
            }
        )
        lot2 = self.env["stock.lot"].create(
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

    def test_lot_propagation(self):
        # Required for `route_id` to be visible in the view
        self.env.user.groups_id += self.env.ref("stock.group_adv_location")

        # Create a sales order with a line of 200 PCE incoming shipment,
        # with route_id drop shipping
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.customer
        so_form.payment_term_id = self.env.ref(
            "account.account_payment_term_end_following_month"
        )
        with mute_logger("odoo.tests.common.onchange"):
            # otherwise complains that there's not enough inventory and
            # apparently that's normal according to @jco and @sle
            with so_form.order_line.new() as line:
                line.product_id = self.external_serial_product
                line.product_uom_qty = 200
                line.price_unit = 1.00
                line.route_id = self.env.ref("purchase_stock.route_warehouse0_buy")

        sale_order_drp_shpng = so_form.save()
        sale_order_drp_shpng.order_line.lot_id = self.env["stock.lot"].create(
            {
                "name": "Seq test DS pdt",
                "product_id": self.external_serial_product.id,
            }
        )
        initial_lot = sale_order_drp_shpng.order_line.lot_id
        # Confirm sales order
        sale_order_drp_shpng.action_confirm()

        # Check a quotation was created to a certain vendor
        # and confirm so it becomes a confirmed purchase order
        purchase = self.env["purchase.order"].search(
            [("partner_id", "=", self.supplier.id)]
        )
        self.assertEqual(purchase.state, "draft")
        self.assertTrue(purchase.order_line.lot_id)
        self.assertEqual(purchase.order_line.lot_id, initial_lot)
        purchase.button_confirm()
        purchase.button_approve()
        self.assertTrue(purchase.picking_ids.move_ids.restrict_lot_id)
        self.assertTrue(purchase.order_line.lot_id)
        self.assertEqual(purchase.order_line.lot_id, initial_lot)
