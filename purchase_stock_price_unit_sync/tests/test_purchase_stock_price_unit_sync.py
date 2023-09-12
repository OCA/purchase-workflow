# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2019 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import TransactionCase, new_test_user, users


class TestProductCostPriceAvcoSync(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
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
                "type": "product",
                "tracking": "none",
                "categ_id": cls.product_category.id,
                "standard_price": 1,
            }
        )

        cls.order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "product_qty": 10.0,
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "date_planned": fields.Date.today(),
                            "price_unit": 8.0,
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
        move = picking.move_lines[:1]
        move.quantity_done = move.product_uom_qty
        picking._action_done()
        svl = move.sudo().stock_valuation_layer_ids[:1]
        self.assertAlmostEqual(svl.unit_cost, 8.0, 2)
        self.order.order_line[:1].price_unit = 6.0
        self.assertAlmostEqual(svl.unit_cost, 6.0, 2)
