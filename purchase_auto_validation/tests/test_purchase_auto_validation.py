# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class CommonAutoPurchaseCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env["res.partner"].create({"name": "supplier"})
        cls.product_isolated = cls.env["product.product"].create(
            {"name": "Product isolated", "type": "product"}
        )
        cls.product_other = cls.env["product.product"].create(
            {"name": "Other product", "type": "product"}
        )
        cls.rule = cls.env["purchase.auto.validation"].create(
            {
                "product_tmpl_ids": [(6, 0, [cls.product_isolated.product_tmpl_id.id])],
                "partner_id": cls.supplier.id,
                "weekday": "0",
                "hour": 14.0,
            }
        )
        route_buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.buy_rule = cls.env["stock.rule"].create(
            {
                "name": "Test Buy Rule",
                "action": "buy",
                "route_id": route_buy.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "company_id": cls.env.company.id,
                "group_propagation_option": "none",
            }
        )

    def _make_procurement(self, product, values, qty=1.0):
        return self.env["procurement.group"].Procurement(
            product,
            qty,
            product.uom_id,
            self.env.ref("stock.stock_location_stock"),
            product.name,
            "TEST",
            self.env.company,
            values,
        )

    def _make_supplierinfo(self, product, partner):
        return self.env["product.supplierinfo"].create(
            {
                "name": partner.id,
                "product_tmpl_id": product.product_tmpl_id.id,
            }
        )

    def _make_procurement_values(self, product, partner):
        supplierinfo = self._make_supplierinfo(product, partner)
        return {
            "date_planned": fields.Datetime.now(),
            "group_id": False,
            "supplierinfo_id": supplierinfo,
        }


class TestAutoPurchase(CommonAutoPurchaseCase):
    def test_isolated_purchase_order(self):
        procurement = self._make_procurement(
            self.product_isolated,
            self._make_procurement_values(self.product_isolated, self.supplier),
        )
        self.env["stock.rule"]._run_buy([(procurement, self.buy_rule)])
        purchase_order = self.env["purchase.order"].search(
            [("purchase_auto_validation_id", "=", self.rule.id)]
        )
        self.assertEqual(len(purchase_order), 1)
        self.assertEqual(purchase_order.order_line.product_id, self.product_isolated)

    def test_constraint_other_product(self):
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "purchase_auto_validation_id": self.rule.id,
            }
        )
        with self.assertRaises(ValidationError) as m:
            purchase_order.write(
                {
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product_other.id,
                                "product_qty": 1,
                            },
                        )
                    ]
                }
            )
        self.assertIn("Only products configured", str(m.exception))

    def test_cron_validates_matching_orders(self):
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "purchase_auto_validation_id": self.rule.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_isolated.id,
                            "product_qty": 1,
                        },
                    )
                ],
            }
        )
        rules = self.rule._get_purchase_to_validate("0", 14)
        self.assertIn(self.rule, rules)
        rules._validate_purchase_orders()
        self.assertEqual(purchase_order.state, "purchase")

    def test_cron_skips_non_matching_day(self):
        rules = self.rule._get_purchase_to_validate("1", 14)
        self.assertNotIn(self.rule, rules)

    def test_second_procurement_same_product_different_qty_merges(self):
        values = self._make_procurement_values(self.product_isolated, self.supplier)
        procurement_1 = self._make_procurement(self.product_isolated, values, qty=1.0)
        self.env["stock.rule"]._run_buy([(procurement_1, self.buy_rule)])
        procurement_2 = self._make_procurement(self.product_isolated, values, qty=2.0)
        self.env["stock.rule"]._run_buy([(procurement_2, self.buy_rule)])
        purchase_orders = self.env["purchase.order"].search(
            [("purchase_auto_validation_id", "=", self.rule.id)]
        )
        self.assertEqual(len(purchase_orders), 1)
        self.assertEqual(len(purchase_orders.order_line), 1)
        self.assertEqual(purchase_orders.order_line.product_qty, 3.0)

    def test_two_products_two_suppliers_separate_orders(self):
        supplier_2 = self.env["res.partner"].create({"name": "supplier 2"})
        product_2 = self.env["product.product"].create(
            {"name": "Product isolated 2", "type": "product"}
        )
        rule_2 = self.env["purchase.auto.validation"].create(
            {
                "product_tmpl_ids": [(6, 0, [product_2.product_tmpl_id.id])],
                "partner_id": supplier_2.id,
                "weekday": "0",
                "hour": 14.0,
            }
        )
        procurement_1 = self._make_procurement(
            self.product_isolated,
            self._make_procurement_values(self.product_isolated, self.supplier),
        )
        procurement_2 = self._make_procurement(
            product_2,
            self._make_procurement_values(product_2, supplier_2),
        )
        self.env["stock.rule"]._run_buy(
            [(procurement_1, self.buy_rule), (procurement_2, self.buy_rule)]
        )
        purchase_orders = self.env["purchase.order"].search(
            [("purchase_auto_validation_id", "in", [self.rule.id, rule_2.id])]
        )
        self.assertEqual(len(purchase_orders), 2)
        self.assertEqual(
            set(purchase_orders.mapped("purchase_auto_validation_id").ids),
            {self.rule.id, rule_2.id},
        )
        order_1 = purchase_orders.filtered(
            lambda po: po.purchase_auto_validation_id == self.rule
        )
        order_2 = purchase_orders.filtered(
            lambda po: po.purchase_auto_validation_id == rule_2
        )
        self.assertEqual(order_1.order_line.product_id, self.product_isolated)
        self.assertEqual(order_2.order_line.product_id, product_2)

    def test_two_products_same_supplier(self):
        procurement_isolated = self._make_procurement(
            self.product_isolated,
            self._make_procurement_values(self.product_isolated, self.supplier),
        )
        procurement_other = self._make_procurement(
            self.product_other,
            self._make_procurement_values(self.product_other, self.supplier),
        )
        self.env["stock.rule"]._run_buy(
            [(procurement_isolated, self.buy_rule), (procurement_other, self.buy_rule)]
        )
        isolated_order = self.env["purchase.order"].search(
            [("purchase_auto_validation_id", "=", self.rule.id)]
        )
        generic_order = self.env["purchase.order"].search(
            [
                ("partner_id", "=", self.supplier.id),
                ("purchase_auto_validation_id", "=", False),
            ]
        )
        self.assertEqual(len(isolated_order), 1)
        self.assertEqual(isolated_order.order_line.product_id, self.product_isolated)
        self.assertEqual(len(generic_order), 1)
        self.assertEqual(generic_order.order_line.product_id, self.product_other)
        self.assertNotEqual(isolated_order, generic_order)

    def test_rule_with_variant_only(self):
        product_variant = self.env["product.product"].create(
            {"name": "Variant only product", "type": "product"}
        )
        rule_variant = self.env["purchase.auto.validation"].create(
            {
                "product_ids": [(6, 0, [product_variant.id])],
                "partner_id": self.supplier.id,
                "weekday": "0",
                "hour": 8.0,
            }
        )
        procurement = self._make_procurement(
            product_variant,
            self._make_procurement_values(product_variant, self.supplier),
        )
        self.env["stock.rule"]._run_buy([(procurement, self.buy_rule)])
        purchase_order = self.env["purchase.order"].search(
            [("purchase_auto_validation_id", "=", rule_variant.id)]
        )
        self.assertEqual(len(purchase_order), 1)
        self.assertEqual(purchase_order.order_line.product_id, product_variant)

    def test_constraint_duplicate_product_same_company(self):
        with self.assertRaises(ValidationError) as m:
            self.env["purchase.auto.validation"].create(
                {
                    "product_tmpl_ids": [
                        (6, 0, [self.product_isolated.product_tmpl_id.id])
                    ],
                    "partner_id": self.supplier.id,
                    "weekday": "1",
                    "hour": 8.0,
                }
            )
        self.assertIn(
            "already covered by another auto purchase validation rule", str(m.exception)
        )

    def test_constraint_duplicate_variant_covered_by_template(self):
        with self.assertRaises(ValidationError) as m:
            self.env["purchase.auto.validation"].create(
                {
                    "product_ids": [(6, 0, [self.product_isolated.id])],
                    "partner_id": self.supplier.id,
                    "weekday": "1",
                    "hour": 8.0,
                }
            )
        self.assertIn(
            "already covered by another auto purchase validation rule", str(m.exception)
        )

    def test_constraint_no_conflict_different_companies(self):
        company_2 = self.env["res.company"].create({"name": "Company 2"})
        rule_company_1 = self.env["purchase.auto.validation"].create(
            {
                "product_tmpl_ids": [(6, 0, [self.product_other.product_tmpl_id.id])],
                "partner_id": self.supplier.id,
                "weekday": "0",
                "hour": 8.0,
                "company_id": self.env.company.id,
            }
        )
        rule_company_2 = self.env["purchase.auto.validation"].create(
            {
                "product_tmpl_ids": [(6, 0, [self.product_other.product_tmpl_id.id])],
                "partner_id": self.supplier.id,
                "weekday": "0",
                "hour": 8.0,
                "company_id": company_2.id,
            }
        )
        self.assertTrue(rule_company_1 and rule_company_2)

    def test_constraint_global_rule_conflicts_with_company_rule(self):
        self.env["purchase.auto.validation"].create(
            {
                "product_tmpl_ids": [(6, 0, [self.product_other.product_tmpl_id.id])],
                "partner_id": self.supplier.id,
                "weekday": "0",
                "hour": 8.0,
                "company_id": self.env.company.id,
            }
        )
        with self.assertRaises(ValidationError) as m:
            self.env["purchase.auto.validation"].create(
                {
                    "product_tmpl_ids": [
                        (6, 0, [self.product_other.product_tmpl_id.id])
                    ],
                    "partner_id": self.supplier.id,
                    "weekday": "1",
                    "hour": 9.0,
                }
            )
        self.assertIn(
            "already covered by another auto purchase validation rule", str(m.exception)
        )
