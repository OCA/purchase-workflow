# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests.common import SavepointCase


class TestQtyCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_model = cls.env["product.product"]

        # Create products:
        cls.p1 = cls.product1 = cls.product_model.create(
            {"name": "Test Product 1", "type": "product", "default_code": "PROD1"}
        )
        p2 = cls.product2 = cls.product_model.create(
            {"name": "Test Product 2", "type": "product", "default_code": "PROD2"}
        )
        cls.date_planned = "2020-04-30 12:00:00"
        partner = cls.env["res.partner"].create({"name": "supplier"})
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.p1.id,
                            "product_uom": cls.p1.uom_id.id,
                            "name": cls.p1.name,
                            "date_planned": cls.date_planned,
                            "product_qty": 42.0,
                            "price_unit": 10.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": p2.id,
                            "product_uom": p2.uom_id.id,
                            "name": p2.name,
                            "date_planned": cls.date_planned,
                            "product_qty": 12.0,
                            "price_unit": 10.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.p1.id,
                            "product_uom": cls.p1.uom_id.id,
                            "name": cls.p1.name,
                            "date_planned": cls.date_planned,
                            "product_qty": 1.0,
                            "price_unit": 10.0,
                        },
                    ),
                ],
            }
        )
