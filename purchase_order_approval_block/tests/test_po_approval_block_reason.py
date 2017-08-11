# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.purchase_order_approval_block.tests.\
    test_purchase_order_approval_block import TestPurchaseOrderApprovalBlock


class TestPoApprovalBlockReason(TestPurchaseOrderApprovalBlock):

    def test_po_approval_block_manual_release(self):
        """Confirming the Blocked PO"""
        # The purchase manager unblocks the RFQ with block
        self.purchase1.sudo(self.user2_id).button_release_approval_block()
        self.assertEquals(self.purchase1.approval_block_id, self.env[
            'purchase.approval.block.reason'])
        # The purchase user validates the RFQ without block
        self.purchase1.sudo(self.user1_id).button_confirm()
        # The PO is approved
        self.assertEquals(self.purchase1.state, 'purchase')

    def test_po_approval_block_to_approve_release(self):
        # The purchase user validates the RFQ with block, and is now to approve
        self.purchase1.sudo(self.user2_id).button_confirm()
        self.assertEquals(self.purchase1.state, 'to approve')
        self.purchase1.sudo(self.user2_id).button_approve(force=False)
        self.assertEquals(self.purchase1.state, 'purchase')
