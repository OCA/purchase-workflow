# Copyright 2026 Marcos Mendez <m@pop.coop>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import TransactionCase


class TestPricelistLastPurchasePrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor"})
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Spare Part",
                "list_price": 1000.0,
                "standard_price": 7.0,
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_unit.id,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Last purchase + 50%",
                "currency_id": cls.env.company.currency_id.id,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "last_purchase_price",
                            "price_markup": 50.0,
                        },
                    )
                ],
            }
        )
        cls.rule = cls.pricelist.item_ids

    def _purchase(self, price, qty=1.0, uom=None, discount=0.0, date=None, **po_vals):
        po = self.env["purchase.order"].create(
            dict(
                {
                    "partner_id": self.vendor.id,
                    "date_order": date or fields.Datetime.now(),
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product.id,
                                "product_qty": qty,
                                "product_uom": (uom or self.uom_unit).id,
                                "price_unit": price,
                                "discount": discount,
                            },
                        )
                    ],
                },
                **po_vals,
            )
        )
        po.button_confirm()
        return po

    def _price(self, product=None, uom=None):
        return self.pricelist._get_product_price(
            product or self.product, 1.0, uom=uom or self.uom_unit
        )

    def test_price_from_last_purchase(self):
        self._purchase(10.0, date="2026-01-01 10:00:00")
        self._purchase(20.0, date="2026-02-01 10:00:00")
        self.assertAlmostEqual(self._price(), 30.0)

    def test_discount_is_applied(self):
        self._purchase(20.0, discount=10.0)
        self.assertAlmostEqual(self._price(), 27.0)

    def test_purchase_uom_is_converted(self):
        self._purchase(120.0, uom=self.uom_dozen)
        self.assertAlmostEqual(self._price(), 15.0)
        self.assertAlmostEqual(self._price(uom=self.uom_dozen), 180.0)

    def test_purchase_currency_is_converted(self):
        currency = self.env["res.currency"].create(
            {"name": "XLP", "symbol": "X", "rounding": 0.01}
        )
        self.env["res.currency.rate"].create(
            {
                "currency_id": currency.id,
                "name": "2000-01-01",
                "rate": 2.0,
                "company_id": self.env.company.id,
            }
        )
        self._purchase(20.0, currency_id=currency.id)
        self.assertAlmostEqual(self._price(), 15.0)

    def test_draft_purchase_is_ignored(self):
        self._purchase(10.0)
        self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "price_unit": 99.0})
                ],
            }
        )
        self.assertAlmostEqual(self._price(), 15.0)

    def test_fallback_to_cost_without_purchase(self):
        self.assertAlmostEqual(self._price(), 10.5)

    def test_template_uses_latest_variant_purchase(self):
        self._purchase(40.0)
        self.assertAlmostEqual(self._price(product=self.product.product_tmpl_id), 60.0)

    def test_template_without_purchase_falls_back_to_cost(self):
        self.assertAlmostEqual(self._price(product=self.product.product_tmpl_id), 10.5)

    def test_price_label(self):
        self.assertIn("last purchase price", self.rule.price)

    def test_other_bases_are_untouched(self):
        self.rule.base = "list_price"
        self.rule.price_markup = 0.0
        self.assertAlmostEqual(self._price(), 1000.0)
        self.assertIn("sales price", self.rule.price)

    def test_purchase_of_other_company_is_ignored(self):
        company_a = self.env.company
        company_b = self.env["res.company"].create(
            {"name": "Company B", "currency_id": company_a.currency_id.id}
        )
        self.env.user.company_ids |= company_b
        self._purchase(10.0, date="2026-01-01 10:00:00")
        self.env = self.env(
            context=dict(self.env.context, allowed_company_ids=company_b.ids)
        )
        self._purchase(100.0, date="2026-02-01 10:00:00", company_id=company_b.id)
        self.env = self.env(
            context=dict(
                self.env.context,
                allowed_company_ids=(company_a | company_b).ids,
            )
        )
        # Shared pricelist: the purchases of the current company only.
        self.assertAlmostEqual(self._price(), 15.0)
        # Pricelist of a company: the purchases of that company only.
        self.pricelist.company_id = company_b
        self.assertAlmostEqual(self._price(), 150.0)
        self.pricelist.company_id = company_a
        self.assertAlmostEqual(self._price(), 15.0)
