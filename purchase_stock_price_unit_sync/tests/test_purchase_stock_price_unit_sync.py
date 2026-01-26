# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2019 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, fields
from odoo.tests import new_test_user, users

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT, BaseCommon


class TestProductCostPriceAvcoSync(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product_category = cls.env["product.category"].create(
            {
                "name": "Category property_cost_method average",
                "property_cost_method": "average",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product for test",
                "is_storable": True,
                "type": "consu",
                "tracking": "none",
                "categ_id": cls.product_category.id,
                "standard_price": 1,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product for test 2",
                "is_storable": True,
                "tracking": "serial",
            }
        )
        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "Product for test 3",
                "is_storable": True,
                "tracking": "serial",
            }
        )

        cls.order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": "Test line",
                            "product_qty": 10.0,
                            "product_id": cls.product.id,
                            "product_uom_id": cls.product.uom_id.id,
                            "date_planned": fields.Date.today(),
                            "price_unit": 8.0,
                        },
                    ),
                    Command.create(
                        {
                            "name": "Test line with kit product",
                            "product_qty": 5.0,
                            "product_id": cls.product_2.id,
                            "product_uom_id": cls.product_2.uom_id.id,
                            "date_planned": fields.Date.today(),
                            "price_unit": 15.0,
                        },
                    ),
                ],
            }
        )
        new_test_user(
            cls.env, login="test-purchase-user", groups="purchase.group_purchase_user"
        )

    @users("test-purchase-user")
    def test_sync_cost_price(self):
        self.order = self.order.with_user(self.env.user)
        self.order.button_confirm()
        picking = self.order.picking_ids[:1]
        move = picking.move_ids[:1]
        move.quantity = move.product_uom_qty
        move.picked = True
        picking._action_done()
        self.order.order_line[:1].price_unit = 6.0
        self.order.order_line[1].price_unit = 12.0
        self.assertAlmostEqual(move.price_unit, 6.0, 2)

    def test_sync_without_move_done(self):
        self.order = self.order.with_user(self.env.user)
        self.order.button_confirm()
        move = self.order.picking_ids.move_ids[:1]
        self.order.order_line[:1].price_unit = 7.0
        self.assertEqual(move.price_unit, 7.0, 2)
        picking = self.order.picking_ids
        move.quantity = move.product_uom_qty
        move.picked = True
        picking._action_done()
        self.order.order_line[:1].with_context(skip_update_price_unit=True).write(
            {"price_unit": 10, "discount": 1}
        )
        self.assertEqual(move.price_unit, 7.0, 2)
        self.order.order_line[:1].write({"discount": 1})
        self.assertNotEqual(move.price_unit, 7.0, 2)
