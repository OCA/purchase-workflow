# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.purchase_order_approval_block.tests.\
    test_purchase_order_approval_block import TestPurchaseOrderApprovalBlock


class TestPoApprovalBlockReason(TestPurchaseOrderApprovalBlock):

    def test_po_approval_block_manual_release(self):
        """Confirming the Blocked PO"""
        # Create a PO
        purchase = self._create_purchase(
            [(self.product1, 1),
             (self.product2, 5),
             (self.product3, 8)])

        purchase.approval_block_id = self.po_approval_block_reason.id

        self.assertEqual(purchase.approval_blocked, True)
        # The purchase manager unblocks the RFQ with block
        purchase.sudo(self.user2_id).button_release_approval_block()
        self.assertEqual(purchase.approval_block_id, self.env[
            'purchase.approval.block.reason'])
        # The purchase user validates the RFQ without block
        purchase.sudo(self.user1_id).button_confirm()
        # The PO is approved
        self.assertEqual(purchase.state, 'purchase')

    def test_po_approval_block_to_approve_release_01(self):
        # Create a PO
        purchase = self._create_purchase(
            [(self.product1, 1),
             (self.product2, 5),
             (self.product3, 8)])

        purchase.approval_block_id = self.po_approval_block_reason.id
        # The purchase user validates the RFQ with block, and is now to approve
        purchase.sudo(self.user2_id).button_confirm()
        self.assertEquals(purchase.state, 'to approve')

        # Simulation the opening of the wizard purchase_exception_confirm and
        # set ignore_exception to True
        po_except_confirm = \
            self.env['purchase.exception.confirm'].with_context(
                {
                    'active_id': purchase.id,
                    'active_ids': [purchase.id],
                    'active_model': purchase._name
                }).create({'ignore': True})
        po_except_confirm.action_confirm()

        self.assertEqual(purchase.state, 'purchase')

    def test_po_approval_block_to_approve_release_02(self):
        # Create a PO
        purchase = self._create_purchase(
            [(self.product1, 1),
             (self.product2, 5),
             (self.product3, 8)])

        purchase.approval_block_id = self.po_approval_block_reason.id
        # The purchase user validates the RFQ with block, and is now to approve
        purchase.sudo(self.user2_id).button_confirm()
        self.assertEquals(purchase.state, 'to approve')

        purchase.sudo(self.user2_id).button_approve()

        self.assertEqual(purchase.state, 'purchase')
