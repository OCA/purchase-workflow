# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2015-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import Form, TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPurchaseOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.categ_cost_average = cls.env["product.category"].create(
            {"name": "Average cost method category", "property_cost_method": "average"}
        )
        product_obj = cls.env["product.product"]
        cls.product_1 = product_obj.create(
            {"name": "Test product 1", "categ_id": cls.categ_cost_average.id}
        )
        cls.product_2 = product_obj.create({"name": "Test product 2"})
        po_model = cls.env["purchase.order.line"]
        currency_rate_model = cls.env["res.currency.rate"]
        # Set the Exchange rate for the currency of the company to 1
        # to avoid issues with rates
        latest_currency_rate_line = currency_rate_model.search(
            [
                ("currency_id", "=", cls.env.user.company_id.currency_id.id),
                ("name", "=", fields.Date.today()),
            ],
            limit=1,
        )
        if latest_currency_rate_line and latest_currency_rate_line.rate != 1.0:
            latest_currency_rate_line.rate = 1.0
        elif not latest_currency_rate_line:
            currency_rate_model.create(
                {
                    "currency_id": cls.env.user.company_id.currency_id.id,
                    "rate": 1.00,
                    "name": fields.Date.today(),
                }
            )
        cls.purchase_order = cls.env["purchase.order"].create(
            {"partner_id": cls.env.ref("base.res_partner_3").id}
        )
        cls.po_line_1 = po_model.create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product_1.id,
                "date_planned": fields.Datetime.now(),
                "name": "Test",
                "product_qty": 1.0,
                "product_uom": cls.product_1.uom_id.id,
                "discount": 50.0,
                "price_unit": 10.0,
                "taxes_id": [],
            }
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "account_type": "expense",
            }
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Sample tax 15%",
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "amount": 15.0,
                "invoice_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.account.id,
                        },
                    ),
                ],
            }
        )
        cls.po_line_2 = po_model.create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product_2.id,
                "date_planned": fields.Datetime.now(),
                "name": "Test",
                "product_qty": 10.0,
                "product_uom": cls.product_2.uom_id.id,
                "discount": 30,
                "taxes_id": [(6, 0, [cls.tax.id])],
                "price_unit": 230.0,
            }
        )
        cls.po_line_3 = po_model.create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product_2.id,
                "date_planned": fields.Datetime.now(),
                "name": "Test",
                "product_qty": 1.0,
                "product_uom": cls.product_2.uom_id.id,
                "discount": 0,
                "taxes_id": [(6, 0, [cls.tax.id])],
                "price_unit": 10.0,
            }
        )
        cls.po_line_4 = po_model.create(
            {
                "order_id": cls.purchase_order.id,
                "display_type": "line_section",
                "name": "Test Section",
                "product_qty": 0.0,
                "product_uom_qty": 0.0,
            }
        )

    def test_purchase_order_vals(self):
        self.assertEqual(self.po_line_1.price_subtotal, 5.0)
        self.assertEqual(self.po_line_2.price_subtotal, 1610.0)
        self.assertEqual(self.po_line_3.price_subtotal, 10.0)
        self.assertEqual(self.purchase_order.amount_untaxed, 1625.0)
        self.assertEqual(self.purchase_order.amount_tax, 243)
        # Change price to launch a recalculation of totals
        self.po_line_1.discount = 60
        self.assertEqual(self.po_line_1.price_subtotal, 4.0)
        self.assertEqual(self.purchase_order.amount_untaxed, 1624.0)
        self.assertEqual(self.purchase_order.amount_tax, 243)

    def test_move_price_unit(self):
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids
        moves = picking.move_ids
        move1 = moves.filtered(lambda x: x.purchase_line_id == self.po_line_1)
        self.assertEqual(move1.price_unit, 5)
        move2 = moves.filtered(lambda x: x.purchase_line_id == self.po_line_2)
        self.assertEqual(move2.price_unit, 161)
        move3 = moves.filtered(lambda x: x.purchase_line_id == self.po_line_3)
        self.assertEqual(move3.price_unit, 10)
        # Confirm the picking to see the cost price
        move1.move_line_ids.qty_done = 1
        picking._action_done()
        self.assertAlmostEqual(self.product_1.standard_price, 5.0)
        # Check data in PO remains the same - This is due to the hack
        self.assertAlmostEqual(self.po_line_1.price_unit, 10.0)
        self.assertAlmostEqual(self.po_line_1.discount, 50.0)

    def test_move_price_unit_discount_sync(self):
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids
        moves = picking.move_ids
        self.po_line_1.discount = 25
        self.po_line_2.discount = 50
        self.po_line_3.discount = 10
        move1 = moves.filtered(lambda x: x.purchase_line_id == self.po_line_1)
        self.assertEqual(move1.price_unit, 7.5)
        move2 = moves.filtered(lambda x: x.purchase_line_id == self.po_line_2)
        self.assertEqual(move2.price_unit, 115.0)
        move3 = moves.filtered(lambda x: x.purchase_line_id == self.po_line_3)
        self.assertEqual(move3.price_unit, 9.0)
        self.po_line_1.price_unit = 1000
        self.po_line_2.price_unit = 500
        self.po_line_3.price_unit = 250
        move1 = moves.filtered(lambda x: x.purchase_line_id == self.po_line_1)
        self.assertEqual(move1.price_unit, 750.0)
        move2 = moves.filtered(lambda x: x.purchase_line_id == self.po_line_2)
        self.assertEqual(move2.price_unit, 250.0)
        move3 = moves.filtered(lambda x: x.purchase_line_id == self.po_line_3)
        self.assertEqual(move3.price_unit, 225.0)

    def test_report_price_unit(self):
        rec = self.env["purchase.report"].search(
            [("product_id", "=", self.product_1.id)]
        )
        self.assertEqual(rec.price_total, 5)
        self.assertEqual(rec.discount, 50)

    def test_no_product(self):
        purchase_form = Form(self.purchase_order)
        with purchase_form.order_line.edit(3) as line:
            line.product_qty = 0.0
        self.assertEqual(self.po_line_4.discount, 0.0)

    def test_invoice(self):
        invoice = self.env["account.move"].new(
            {
                "move_type": "out_invoice",
                "partner_id": self.env.ref("base.res_partner_3").id,
                "purchase_id": self.purchase_order.id,
            }
        )
        invoice._onchange_purchase_auto_complete()
        line = invoice.invoice_line_ids.filtered(
            lambda x: x.purchase_line_id == self.po_line_1
        )
        self.assertEqual(line.discount, 50)
        line = invoice.invoice_line_ids.filtered(
            lambda x: x.purchase_line_id == self.po_line_2
        )
        self.assertEqual(line.discount, 30)
        line = invoice.invoice_line_ids.filtered(
            lambda x: x.purchase_line_id == self.po_line_3
        )
        self.assertEqual(line.discount, 0)
