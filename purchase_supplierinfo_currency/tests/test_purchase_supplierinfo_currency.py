# Copyright 2023 Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseSupplierinfoCurrency(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Supplier PSC"})
        cls.currency_usd = cls.env.ref("base.USD")
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.currency_usd.active = True
        cls.currency_eur.active = True
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.stock_rule = cls.env.ref("purchase_stock.route_warehouse0_buy").rule_ids[0]
        cls.origin = "Test PSC Procurement"
        cls.prev_orders = cls.env["purchase.order"].search(
            [("origin", "=", cls.origin)]
        )
        cls.values_base = {
            "company_id": cls.env.user.company_id,
            "date_planned": fields.Datetime.now(),
        }

    def _create_product(self, name, currency):
        return self.env["product.product"].create(
            {
                "name": name,
                "type": "product",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.partner.id,
                            "min_qty": 1.0,
                            "price": 100.0,
                            "currency_id": currency.id,
                        },
                    )
                ],
            }
        )

    def _run_procurement(self, product):
        procurement_group = self.env["procurement.group"]
        procurement = procurement_group.Procurement(
            product,
            1.0,
            product.uom_id,
            self.stock_location,
            False,
            self.origin,
            self.env.company,
            self.values_base,
        )
        rule = procurement_group._get_rule(
            procurement.product_id, procurement.location_id, procurement.values
        )
        self.stock_rule._run_buy([(procurement, rule)])

    def _get_new_orders(self):
        return self.env["purchase.order"].search(
            [("origin", "=", self.origin), ("id", "not in", self.prev_orders.ids)]
        )

    def test_domain_includes_currency_when_supplier_has_currency(self):
        """_make_po_get_domain adds currency_id filter when supplier has a currency."""
        supplier = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "currency_id": self.currency_usd.id,
                "price": 100.0,
            }
        )
        values = dict(self.values_base, supplier=supplier)
        domain = self.stock_rule._make_po_get_domain(
            self.env.user.company_id, values, self.partner
        )
        self.assertIn(("currency_id", "=", self.currency_usd.id), domain)

    def test_po_currency_matches_supplier_currency(self):
        """Procurement creates a PO using the supplier's currency."""
        product = self._create_product("Product USD", self.currency_usd)
        self._run_procurement(product)
        orders = self._get_new_orders()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders.currency_id, self.currency_usd)

    def test_different_currencies_create_separate_pos(self):
        """Products with different supplier currencies generate separate POs."""
        product_usd = self._create_product("Product USD", self.currency_usd)
        product_eur = self._create_product("Product EUR", self.currency_eur)
        self._run_procurement(product_usd)
        self._run_procurement(product_eur)
        orders = self._get_new_orders()
        self.assertEqual(len(orders), 2)
        currencies = orders.mapped("currency_id")
        self.assertIn(self.currency_usd, currencies)
        self.assertIn(self.currency_eur, currencies)

    def test_same_currency_groups_into_one_po(self):
        """Products with the same supplier currency are grouped into a single PO."""
        product_1 = self._create_product("Product 1 USD", self.currency_usd)
        product_2 = self._create_product("Product 2 USD", self.currency_usd)
        self._run_procurement(product_1)
        self._run_procurement(product_2)
        orders = self._get_new_orders()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders.currency_id, self.currency_usd)
        self.assertEqual(len(orders.order_line), 2)
