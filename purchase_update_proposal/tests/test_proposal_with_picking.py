# © 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class Test(common.TransactionCase):
    """Test here are done when purchase is confirmed and partially delivered"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Manage purchase
        cls.order = cls.env.ref("purchase_update_proposal.purchase_order")
        cls.order.button_confirm()
        # Generate partial delivery
        picking = cls.order.picking_ids[0]
        moves = picking.move_line_ids
        moves[0].write({"qty_done": 1})
        backorder_wiz = picking.button_validate()
        common.Form(
            cls.env[backorder_wiz["res_model"]].with_context(**backorder_wiz["context"])
        ).save().process()
        # select purchase lines
        cls.lamp_line = cls.order.order_line.filtered(
            lambda s: s.product_id.default_code == "FURN_8888"
        )
        cls.other_line = cls.order.order_line.filtered(
            lambda s: s.product_id.default_code == "FURN_7777"
        )  # Chair line

    def test_received_field(self):
        order = self.order
        pick = order.picking_ids.filtered(lambda s: s.state == "done")
        line = order.order_line.filtered(
            lambda s: s.product_id == pick.move_ids[0].product_id
        )
        assert line.received == "partially"
        assert order.partially_received is True

    def test_date_field(self):
        order = self.get_order_with_user(alternate_user=True)
        assert self.lamp_line.received == "partially"
        assert self.other_line.received == ""
        # Lamp product line
        self.lamp_line.button_update_proposal()
        order.proposal_ids[0].date = "2900-01-07"
        order.submit_proposal()
        # order has grant to submit but not for approve
        self.order.approve_proposal()
        assert self.lamp_line.date_planned.strftime(DF) == "2900-01-07"
        # other product
        self.other_line.button_update_proposal()
        order.proposal_ids[0].date = "2900-01-08"
        self.order.approve_proposal()
        assert self.other_line.date_planned.strftime(DF) == "2900-01-08"

    def test_price_field(self):
        order = self.get_order_with_user(alternate_user=True)
        # Lamp product line
        self.lamp_line.button_update_proposal()
        order.proposal_ids[0].price_u = 99
        self.order.approve_proposal()
        # other product
        self.other_line.button_update_proposal()
        order.proposal_ids[0].price_u = 98
        self.order.approve_proposal()
        assert self.other_line.price_unit == 98

    def test_qty_field(self):
        order = self.get_order_with_user(alternate_user=True)
        # Lamp product line
        self.lamp_line.button_update_proposal()
        order.proposal_ids[0].qty = 99
        self.order.approve_proposal()
        assert self.lamp_line.product_qty != 99
        self.order.reset_proposal()
        order.proposal_ids[0].unlink()
        # other product
        self.other_line.button_update_proposal()
        order.proposal_ids[0].qty = 97
        order.submit_proposal()
        self.order.approve_proposal()
        assert self.other_line.product_qty != 97
        assert self.order.proposal_state == "draft"
        assert self.order.proposal_updatable == "no"

    def test_populate_all_lines(self):
        order = self.get_order_with_user(alternate_user=True)
        order.populate_all_purchase_lines()
        # all not completely delivered lines are able to be updated
        assert len(order.proposal_ids) == 2

    def get_order_with_user(self, alternate_user=None):
        order = self.order
        if alternate_user:
            order = order.with_user(
                self.env.ref("purchase_update_proposal.supplier_demo_user").id
            )
        return order
