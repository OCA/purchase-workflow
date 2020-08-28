# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, SavepointCase


class TestDelay(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestDelay, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.supplier = cls.env["res.partner"].create({"name": "supplier test"})

    def test_set_delay_from_form(self):
        form = Form(self.env["product.supplierinfo"])
        form.name = self.supplier
        # test compute method
        form.transport_delay = 5
        self.assertEqual(form.delay, 5)
        form.supplier_delay = 5
        self.assertEqual(form.delay, 10)
        form.save()

    def test_set_delay_from_create(self):
        record = self.env["product.supplierinfo"].create(
            {"name": self.supplier.id, "transport_delay": 5, "supplier_delay": 5}
        )
        # test compute method
        self.assertEqual(record.transport_delay, 5)
        self.assertEqual(record.supplier_delay, 5)
        self.assertEqual(record.delay, 10)
        # test inverse method
        record.delay = 12
        self.assertEqual(record.transport_delay, 5)
        self.assertEqual(record.supplier_delay, 7)
        self.assertEqual(record.delay, 12)
        # Should raise an exception when delay < transport_delay
        with self.assertRaises(ValidationError):
            record.delay = 3

    def test_set_delay_from_create_with_delay(self):
        record = self.env["product.supplierinfo"].create(
            {
                "name": self.supplier.id,
                "transport_delay": 5,
                "supplier_delay": 5,
                "delay": 12,
            }
        )
        # test compute method: 'delay' takes the precedence over other fields
        self.assertEqual(record.transport_delay, 5)
        self.assertEqual(record.supplier_delay, 7)
        self.assertEqual(record.delay, 12)
