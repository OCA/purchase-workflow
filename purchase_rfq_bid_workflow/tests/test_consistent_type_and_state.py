from openerp.tests import common


class TestConsistentTypeAndState(common.TransactionCase):
    def test_all_approved_are_purchases(self):
        PO = self.env['purchase.order']
        self.assertFalse(PO.search([
            ('state', '=', 'approved'),
            ('type', '!=', 'purchase'),
        ]))
