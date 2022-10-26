import odoo.tests.common as common
from odoo.tests import Form


class TestSaleOrderLineDescriptionChange(common.TransactionCase):
    def setUp(self):
        super(TestSaleOrderLineDescriptionChange, self).setUp()
        self.purchase_order_model = self.env["purchase.order"]
        self.pt_model = self.env["product.template"]
        self.partner = self.env.ref("base.res_partner_12")
        self.purchase = self.purchase_order_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
            }
        )

        self.attribute_1 = self.env["product.attribute"].create(
            {
                "name": "Density",
            }
        )
        self.value_1 = self.env["product.attribute.value"].create(
            {
                "name": "High",
                "attribute_id": self.attribute_1.id,
            }
        )
        self.value_2 = self.env["product.attribute.value"].create(
            {
                "name": "Low",
                "attribute_id": self.attribute_1.id,
            }
        )

        self.attribute_2 = self.env["product.attribute"].create(
            {
                "name": "Fragrance",
            }
        )
        self.value_2_1 = self.env["product.attribute.value"].create(
            {
                "name": "Nice",
                "attribute_id": self.attribute_2.id,
            }
        )

        self.product_template = self.pt_model.create(
            {
                "name": "Test product",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attribute_1.id,
                            "value_ids": [(6, 0, (self.value_1 + self.value_2).ids)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attribute_2.id,
                            "value_ids": [(6, 0, self.value_2_1.ids)],
                        },
                    ),
                ],
            }
        )

    def test_check_purchase_order_line_single_atr_description(self):
        purchase_form = Form(self.purchase)
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = self.product_template.product_variant_ids[0]
        purchase_form.save()
        self.assertIn("Nice", self.purchase.order_line.name)
