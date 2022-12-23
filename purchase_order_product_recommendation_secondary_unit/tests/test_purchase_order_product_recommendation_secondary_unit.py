# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form, TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestPurchaseOrderProductRecommendationSecondaryUnit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Active multiple units of measure security group for user
        cls.env.user.groups_id = [(4, cls.env.ref("uom.group_uom").id)]
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.product = cls._create_product_with_secondary_unit(cls)
        cls.product.purchase_secondary_uom_id = cls.product.secondary_uom_ids
        cls.purchase_order = cls._create_purchase_order(cls)
        cls.purchase_order.button_confirm()
        # Create a purchase order for the same customer
        cls.new_po = cls.env["purchase.order"].create({"partner_id": cls.partner.id})

    def _create_product_with_secondary_unit(self):
        product = Form(self.env["product.product"])
        product.name = "Test product"
        product.detailed_type = "product"
        product.uom_id = self.env.ref("uom.product_uom_kgm")
        product.uom_po_id = self.env.ref("uom.product_uom_kgm")
        with product.secondary_uom_ids.new() as line:
            line.code = "PQ1-5"
            line.name = "Package of"
            line.uom_id = self.env.ref("uom.product_uom_kgm")
            line.factor = 1.5
        return product.save()

    def _create_purchase_order(self):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_qty = 10
            line_form.price_unit = 100.00
        return order_form.save()

    def wizard(self):
        """Get a wizard."""
        wizard = (
            self.env["purchase.order.recommendation"]
            .with_context(active_id=self.new_po.id, active_model="purchase.order")
            .create({})
        )
        wizard._generate_recommendations()
        return wizard

    def test_recommendation_secondary_unit(self):
        wizard = self.wizard()
        wizard.show_all_partner_products = True
        wizard._generate_recommendations()
        self.assertEqual(
            wizard.line_ids.secondary_uom_id, self.product.secondary_uom_ids
        )
