import unittest2

from ..purchase_group_hooks import PurchaseOrder


class TestGroupOrders(unittest2.TestCase):

    def setUp(self):
        super(TestGroupOrders, self).setUp()

    def test_no_orders(self):
        """Group an empty list of orders as an empty dictionary."""

        grouped = PurchaseOrder._group_orders([])
        self.assertEquals(grouped, {})
