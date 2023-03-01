# © 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class Test(common.SavepointCase):
    """Test here are done when purchase is confirmed and partially delivered"""

    @classmethod
    def setUpClass(self):
        super(Test, self).setUpClass()
        # Manage purchase
        self.order = self.env.ref("purchase_update_proposal.purchase_order")
        self.order.signal_workflow("purchase_confirm")
        # Generate partial delivery
        picking = self.order.picking_ids[0]
        wiz = (
            self.env["stock.transfer_details"]
            .with_context(active_model=picking._name, active_ids=[picking.id])
            .create({"picking_id": picking.id})
        )
        wiz.item_ids.filtered(lambda s: s.product_id.default_code != "DVD").unlink()
        line = wiz.item_ids.filtered(lambda s: s.product_id.default_code == "DVD")
        line.quantity = 1
        wiz.do_detailed_transfer()
        # select purchase lines
        self.dvd_line = self.order.order_line.filtered(
            lambda s: s.product_id.default_code == "DVD"
        )
        self.other_line = self.order.order_line.filtered(
            lambda s: s.product_id.default_code != "DVD"
        )

    def test_received_field(self):
        order = self.order
        pick = order.picking_ids.filtered(lambda s: s.state == "done")
        line = order.order_line.filtered(
            lambda s: s.product_id == pick.move_lines[0].product_id
        )
        assert line.received == "partially"
        assert order.partially_received is True

    def test_date_field(self):
        order = self.get_order_with_user(alternate_user=True)
        assert self.dvd_line.received == "partially"
        assert self.other_line.received == ""
        # DVD product line
        self.dvd_line.button_update_proposal()
        order.proposal_ids[0].date = "2900-01-07"
        order.submit_proposal()
        # order has grant to submit but not for approve
        self.order.approve_proposal()
        assert self.dvd_line.date_planned == "2900-01-07"
        # other product
        self.other_line.button_update_proposal()
        order.proposal_ids[0].date = "2900-01-08"
        self.order.approve_proposal()
        assert self.other_line.date_planned == "2900-01-08"

    def test_price_field(self):
        order = self.get_order_with_user(alternate_user=True)
        # DVD product line
        self.dvd_line.button_update_proposal()
        order.proposal_ids[0].price_u = 99
        self.order.approve_proposal()
        # other product
        self.other_line.button_update_proposal()
        order.proposal_ids[0].price_u = 98
        self.order.approve_proposal()
        assert self.other_line.price_unit == 98

    def test_qty_field(self):
        order = self.get_order_with_user(alternate_user=True)
        # DVD product line
        self.dvd_line.button_update_proposal()
        order.proposal_ids[0].qty = 99
        self.order.approve_proposal()
        assert self.dvd_line.product_qty != 99
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
            order = order.sudo(
                user=self.env.ref("purchase_update_proposal.supplier_demo_user").id
            )
        return order
