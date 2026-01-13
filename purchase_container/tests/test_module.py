from odoo import Command, fields

from odoo.addons.base.tests.common import BaseCommon


class Test(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Supplier"})
        # Create product template first with base_unit_count for Kencove requirement
        product_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "base_unit_count": 1,
            }
        )
        cls.product = product_tmpl.product_variant_id
        cls.cont_a = cls.env["purchase.container"].create({"code": "AA"})
        cls.cont_b = cls.env["purchase.container"].create({"code": "BB"})
        cls.incoterm_id = cls.env.ref("account.incoterm_FCA")

    def _validate_picking(self, picking):
        """Helper to validate picking by setting quantities and validating."""
        for move in picking.move_ids:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()

    def test_container_by_purchase(self):
        # first PO
        po = self.get_po()
        po.button_confirm()
        pick01 = po.picking_ids[0]
        pick01.container_id = self.cont_a.id
        self.assertIn(self.cont_a, po.container_ids)
        self.assertEqual(self.cont_a.purchase_order_count, 1)
        self._validate_picking(pick01)
        # this update triggers a new picking
        po.order_line[0].product_qty = 7
        pick02 = po.picking_ids.filtered(lambda x: x.state != "done")
        pick02.container_id = self.cont_b.id
        self._validate_picking(pick02)
        self.assertEqual(pick02.state, "done")
        self.assertIn(self.cont_b, po.container_ids)
        self.assertEqual(self.cont_b.purchase_order_count, 1)
        # second PO
        po2 = po.copy()
        po2.button_confirm()
        pick11 = po2.picking_ids
        pick11.container_id = self.cont_b.id
        self._validate_picking(pick11)
        self.assertIn(self.cont_b, po2.container_ids)
        self.assertEqual(pick11.state, "done")
        self.assertEqual(len(self.cont_b.purchase_order_ids), 2)
        self.assertEqual(self.cont_b.purchase_order_count, 1)
        # this method is not computed because not a stored field
        self.cont_b._compute_purchase_order_count()
        self.assertEqual(self.cont_b.purchase_order_count, 2)

        self.cont_b._compute_incoterm_id()
        self.assertEqual(self.cont_b.displayed_incoterm_id, self.incoterm_id)

    def test_action_views(self):
        po = self.get_po()
        po.button_confirm()
        pick01 = po.picking_ids[0]
        pick01.container_id = self.cont_a.id
        self.cont_a.action_view_rfq()
        self.cont_a.action_view_order()
        self.cont_a.action_view_picking()

    def get_po(self):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "date_planned": fields.Datetime.now(),
                "incoterm_id": self.incoterm_id.id,
                "order_line": [
                    Command.create(
                        {
                            "name": "Test Line",
                            "product_id": self.product.id,
                            "product_qty": 4.0,
                            "product_uom": self.product.uom_po_id.id,
                            "price_unit": 1,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
