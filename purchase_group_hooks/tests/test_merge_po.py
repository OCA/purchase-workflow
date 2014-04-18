import unittest2
from mock import Mock

from ..purchase_group_hooks import PurchaseOrder


class TestGroupOrders(unittest2.TestCase):

    def setUp(self):
        super(TestGroupOrders, self).setUp()
        self.order1 = Mock()
        self.order2 = Mock()

    def test_no_orders(self):
        """Group an empty list of orders as an empty dictionary."""

        grouped = PurchaseOrder._group_orders([])
        self.assertEquals(grouped, {})

    def test_one_order(self):
        """A single order will not be grouped."""
        grouped = PurchaseOrder._group_orders([self.order1])
        self.assertEquals(grouped, {})
