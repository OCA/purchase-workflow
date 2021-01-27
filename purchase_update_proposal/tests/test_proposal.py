# -*- coding: utf-8 -*-
# © 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
from openerp.exceptions import Warning as UserError


class Test(common.SavepointCase):
    @classmethod
    def setUpClass(self):
        super(Test, self).setUpClass()
        order = self.env.ref("purchase.purchase_order_7")
        order.signal_workflow("purchase_confirm")
        self.order_basic = order
        order = self.env.ref("purchase_update_proposal.purchase_order")
        order.signal_workflow("purchase_confirm")
        self.order_main = order

    def test_basics(self):
        order = self.order_basic
        assert len(order.order_line) == 2
        order.order_line[0].button_update_proposal()
        order.order_line[1].button_update_proposal()
        order.order_line[0].button_update_proposal()
        prop1 = order.proposal_ids[0]
        prop2 = order.proposal_ids[1]
        prop3 = order.proposal_ids[2]
        assert prop1.qty == order.order_line[0].product_qty
        assert prop1.date is False
        assert prop3.qty == order.order_line[0].product_qty
        old1qty = prop1.qty
        prop1.write({"qty": prop1.qty - 1})
        prop2.write({"qty": prop2.qty - 1})
        prop3.write({"qty": 1})
        order.approve_proposal()
        assert len(order.order_line) == 3
        assert order.order_line[2].product_qty == 1
        assert order.order_line[0].product_qty == old1qty - 1

    def test_populate_complete_missing_lines(self):
        order = self.get_order_with_user(alternate_user=True)
        order.order_line[1].button_update_proposal()
        # Only missing lines should be added
        order.populate_all_purchase_lines()
        assert order.proposal_count == len(order.order_line)

    def test_mass_update_date(self):
        "Update all lines of proposal_ids"
        order = self.get_order_with_user(alternate_user=True)
        order.populate_all_purchase_lines()
        order.proposal_date = "2050-01-01"
        order.onchange_proposal_date()
        dates = [x.date for x in order.proposal_ids]
        assert len(dates) == 2
        dates = set([x.date for x in order.proposal_ids])
        assert len(dates) == 1
        assert order.proposal_date == list(dates)[0]

    def test_proposal_workflow(self):
        # order with supplier
        order = self.get_order_with_user()
        order.partner_id.write({"check_price_on_proposal": True})
        order_s = self.get_order_with_user(alternate_user=True)
        order_s.order_line[0].button_update_proposal()
        prop = order_s.proposal_ids[0]
        prop.write({"qty": 10, "price_u": 2})
        order_s.submit_proposal()
        assert order_s.proposal_updatable == "yes"
        assert order.proposal_state == "submitted"
        order.approve_proposal()
        # We check all is correctly written
        assert order.state == "approved"
        assert order.order_line[0].product_qty == 10
        assert order.order_line[0].price_unit == 2

    def test_duplicate_purchase_line(self):
        order = self.get_order_with_user()
        initial_qty = order.order_line[0].product_qty
        order.order_line[0].button_update_proposal()
        order.order_line[0].button_update_proposal()
        assert len(order.proposal_ids) == 2
        order.proposal_ids[0].write({"qty": order.proposal_ids[0].qty - 1})
        order.proposal_ids[1].write({"qty": 1})
        order.submit_proposal()
        order.approve_proposal()
        assert order.order_line[0].product_qty == initial_qty - 1
        assert order.order_line[2].product_qty == 1

    def test_check_purchase_line(self):
        order = self.get_order_with_user()
        order.partner_id.write({"check_price_on_proposal": True})
        order_s = self.get_order_with_user(alternate_user=True)
        order.order_line[0].button_update_proposal()
        order.order_line[0].button_update_proposal()
        order_s.proposal_ids[0].write({"qty": 2})
        order_s.proposal_ids[1].write({"qty": 5, "price_u": 3})
        order.approve_proposal()
        assert order.order_line[0].product_qty == 2
        assert order.order_line[2].product_qty == 5
        assert order.order_line[2].price_unit == 3
        assert order.order_line[2].taxes_id == order.order_line[0].taxes_id

    def test_supplier_should_not_update_forbidden_fields(self):
        order = self.get_order_with_user(alternate_user=True)
        with self.assertRaises(UserError):
            order.write({"partner_ref": "bla"})

    def test_supplier_should_not_approve(self):
        order = self.get_order_with_user(alternate_user=True)
        order.order_line[0].button_update_proposal()
        order.proposal_ids[0].qty = 99
        order.submit_proposal()
        with self.assertRaises(UserError):
            order.approve_proposal()

    def get_order_with_user(self, alternate_user=None):
        order = self.order_main
        if alternate_user:
            order = order.sudo(
                user=self.env.ref("purchase_update_proposal.supplier_demo_user").id
            )
        return order
