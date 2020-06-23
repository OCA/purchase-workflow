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

    def check_delay_equals_delays(self, form):
        delays = form.transport_delay + form.supplier_delay
        self.assertEquals(form.delay, delays)

    def test_set_delays(self):
        form = Form(self.env["product.supplierinfo"])
        form.name = self.supplier
        # test compute method
        form.transport_delay = 5
        self.assertEqual(form.delay, 5)
        self.check_delay_equals_delays(form)
        form.supplier_delay = 5
        self.assertEqual(form.delay, 10)
        self.check_delay_equals_delays(form)

    def test_set_delay(self):
        # Can't use Form here as Form().save() does not saves readonly fields.
        record = self.env["product.supplierinfo"].create(
            {
                "name": self.supplier.id,
                "delay": 10,
                "transport_delay": 5,
                "supplier_delay": 5,
            }
        )
        # test inverse method
        record.delay = 12
        self.assertEqual(record.transport_delay, 5)
        self.assertEqual(record.supplier_delay, 7)
        self.check_delay_equals_delays(record)
        # Should raise an exception when delay < transport_delay
        with self.assertRaises(ValidationError):
            record.delay = 3
