# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields
from odoo.tests import Form, common


class TestPurchaseStockPicking(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency_usd = cls.env.ref("base.USD")
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.account_tax = cls.env["account.tax"].create(
            {"name": "0%", "amount_type": "fixed", "type_tax_use": "sale", "amount": 0}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner test"})
        cls.product_category = cls.env["product.category"].create(
            {"name": "Category test", "property_cost_method": "average"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
                "categ_id": cls.product_category.id,
                "taxes_id": [(6, 0, [cls.account_tax.id])],
            }
        )
        # Create custom rates to USD + EUR
        cls._create_currency_rate(cls, cls.currency_usd, fields.Date.today(), 1.0)
        cls._create_currency_rate(cls, cls.currency_eur, fields.Date.today(), 2.0)

    def _create_currency_rate(self, currency_id, name, rate):
        self.env["res.currency.rate"].create(
            {"currency_id": currency_id.id, "name": name, "rate": rate}
        )

    def _create_purchase_order(self, currency_id):
        purchase_form = Form(self.env["purchase.order"])
        purchase_form.partner_id = self.partner
        purchase_form.currency_id = currency_id
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.price_unit = 10
        purchase = purchase_form.save()
        purchase.button_confirm()
        return purchase

    def test_01_purchase_usd(self):
        purchase = self._create_purchase_order(self.currency_usd)
        picking = purchase.picking_ids[0]
        self.assertEqual(picking.purchase_currency_id, self.currency_usd)
        self.assertEqual(picking.currency_rate_amount, 1.0)
        picking.move_ids_without_package.quantity_done = 1
        picking.button_validate()
        self.assertEqual(picking.move_lines.stock_valuation_layer_ids.unit_cost, 10)

    def test_02_purchase_eur(self):
        purchase = self._create_purchase_order(self.currency_eur)
        picking = purchase.picking_ids[0]
        self.assertEqual(picking.purchase_currency_id, self.currency_eur)
        self.assertEqual(picking.currency_rate_amount, 2.0)
        picking.move_ids_without_package.quantity_done = 1
        picking.button_validate()
        self.assertEqual(picking.move_lines.stock_valuation_layer_ids.unit_cost, 5)
