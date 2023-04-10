from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase


@tagged("post_install", "-at_install", "standart")
class TestPurchaseOrderLine(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestPurchaseOrderLine, self).setUp(*args, **kwargs)

        self.partner1 = self.env["res.partner"].create({"name": "Test"})
        self.product1 = self.env["product.product"].create({"name": "desktop"})

        self.purchase_order_1 = self.env["purchase.order"].create(
            {"partner_id": self.partner1.id}
        )

        self.tax = self.env["account.tax"].create(
            {
                "name": "Tax 10",
                "type_tax_use": "purchase",
                "amount": 10,
            }
        )
        with Form(self.purchase_order_1) as form:
            with form.order_line.new() as line_1:
                line_1.product_id = self.product1
            form.save()
        self.purchase_order_1.order_line[0].taxes_id = [(6, 0, [self.tax.id])]

    def test_check_field_content(self):
        purchase_order_line = self.purchase_order_1.order_line[0]
        self.assertEqual(
            purchase_order_line.get_field_data("product_id"),
            self.product1.name,
            "Field content must be equal to {name}".format(name=self.product1.name),
        )
        self.assertEqual(
            purchase_order_line.get_field_data("partner_id"),
            self.partner1.name,
            "Field content must be equal to {name}".format(name=self.product1.name),
        )

    def test_check_field_content_m2m(self):
        purchase_order_line = self.purchase_order_1.order_line[0]
        self.assertEqual(
            purchase_order_line.get_field_data("taxes_id"),
            "{name}".format(name=self.tax[0].name),
            "Field content must be equal to {name}".format(name=self.tax[0].name),
        )

    def test_count_rfq_fields(self):
        default_count = len(self.purchase_order_1._default_report_rfq_fields())
        self.assertEqual(
            self.purchase_order_1.report_field_ids.count_rfq_fields(),
            default_count,  # default count fields_rfq
            "Must be equal to {count}".format(count=default_count),
        )

    def test_count_po_fields(self):
        default_count = len(self.purchase_order_1._default_report_po_fields())
        self.assertEqual(
            self.purchase_order_1.report_field_ids.count_po_fields(),
            default_count,  # default count fields_po
            "Must be equal to {count}".format(count=default_count),
        )
