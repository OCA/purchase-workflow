# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.exceptions import UserError
from odoo.tests import common
from odoo.tools import SUPERUSER_ID


class TestPurchaseRequest(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseRequest, self).setUp()
        self.purchase_request_obj = self.env['purchase.request']
        self.purchase_request_line_obj = self.env['purchase.request.line']
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        self.purchase_request = self.purchase_request_obj.create(vals)
        vals = {
            'request_id': self.purchase_request.id,
            'product_id': self.env.ref('product.product_product_13').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 5.0,
        }
        self.purchase_request_line_obj.create(vals)

    def test_purchase_request_status(self):
        """Tests Purchase Request status workflow."""
        purchase_request = self.purchase_request
        self.assertEqual(
            purchase_request.is_editable, True,
            'Should be editable')
        purchase_request.button_to_approve()
        self.assertEqual(
            purchase_request.state, 'to_approve',
            'Should be in state to_approve')
        self.assertEqual(
            purchase_request.is_editable, False,
            'Should not be editable')
        purchase_request.button_draft()
        self.assertEqual(
            purchase_request.is_editable, True,
            'Should be editable')
        self.assertEqual(
            purchase_request.state, 'draft',
            'Should be in state draft')
        purchase_request.button_to_approve()
        purchase_request.button_done()
        self.assertEqual(
            purchase_request.is_editable, False,
            'Should not be editable')
        purchase_request.button_rejected()
        self.assertEqual(
            purchase_request.is_editable, False,
            'Should not be editable')

    def test_auto_reject(self):
        """Tests if a Purchase Request is autorejected when all lines are
        cancelled."""
        purchase_request = self.purchase_request
        # Add a second line to the PR:
        vals = {
            'request_id': purchase_request.id,
            'product_id': self.env.ref('product.product_product_16').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 5.0,
        }
        self.purchase_request_line_obj.create(vals)
        lines = purchase_request.line_ids
        # Cancel one line:
        lines[0].do_cancel()
        self.assertNotEqual(purchase_request.state, 'rejected',
                            'Purchase Request should not have been rejected.')
        # Cancel the second one:
        lines[1].do_cancel()
        self.assertEqual(purchase_request.state, 'rejected',
                         'Purchase Request should have been auto-rejected.')

    def test_pr_line_to_approve_allowed(self):
        request = self.purchase_request
        self.assertTrue(request.to_approve_allowed)

        pr_lines = self.purchase_request.line_ids
        pr_lines.write({'product_qty': 0})
        self.assertFalse(request.to_approve_allowed)

        pr_lines.write({'product_qty': 5})
        self.assertTrue(request.to_approve_allowed)

        pr_lines.do_cancel()
        self.assertFalse(request.to_approve_allowed)

        # Request has been automatically rejected
        request.button_draft()
        new_line = self.purchase_request_line_obj.create({
            'product_id': self.env.ref(
                'product.product_product_16').id,
            'product_uom_id': self.env.ref(
                'product.product_uom_unit').id,
            'product_qty': 0.0,
            'request_id': request.id,
        })
        pr_lines.do_cancel()
        self.assertFalse(request.to_approve_allowed)

        new_line.write({'product_qty': 1})
        self.assertTrue(request.to_approve_allowed)

        request.line_ids.unlink()
        self.assertFalse(request.to_approve_allowed)

    def test_empty_purchase_request(self):
        pr = self.purchase_request
        pr_lines = pr.line_ids
        pr_lines.write({'product_qty': 0})

        with self.assertRaises(UserError):
            self.purchase_request.button_to_approve()

        pr_lines.write({'product_qty': 4})
        pr.button_to_approve()
        self.assertEqual(pr.state, 'to_approve')
