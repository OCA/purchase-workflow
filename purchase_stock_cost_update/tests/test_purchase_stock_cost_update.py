# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
import logging
from functools import partial

from odoo.fields import Date
from odoo.tests import Form, common

_logger = logging.getLogger(__name__)


class PurchasStockCostUpdateCase(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.categ_fruits_avco = cls.env["product.category"].create(
            {
                "name": "Fruits",
                "property_cost_method": "average",
            }
        )
        cls.peach = cls.env["product.product"].create(
            {
                "name": "Peach of Teruel",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_kgm").id,
                "uom_po_id": cls.env.ref("uom.product_uom_kgm").id,
                "categ_id": cls.categ_fruits_avco.id,
            }
        )
        cls.grapes = cls.env["product.product"].create(
            {
                "name": "Moscatel Grapes",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_kgm").id,
                "uom_po_id": cls.env.ref("uom.product_uom_kgm").id,
                "categ_id": cls.categ_fruits_avco.id,
            }
        )
        cls.raspberry = cls.env["product.product"].create(
            {
                "name": "raspberry",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_kgm").id,
                "uom_po_id": cls.env.ref("uom.product_uom_kgm").id,
                "categ_id": cls.categ_fruits_avco.id,
                "tracking": "lot",
            }
        )
        cls.crown_melon = cls.env["product.product"].create(
            {
                "name": "crown_melon",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_kgm").id,
                "uom_po_id": cls.env.ref("uom.product_uom_kgm").id,
                "categ_id": cls.categ_fruits_avco.id,
                "tracking": "lot",
            }
        )
        cls.supplier_frutas_calanda = cls.env["res.partner"].create(
            {
                "name": "Frutas Calanda",
            }
        )
        # Weirdest UoM ever... but it's convenient for our tests
        cls.dekakilogram = cls.env["uom.uom"].create(
            {
                "name": "dakg",
                "category_id": cls.env.ref("uom.product_uom_kgm").category_id.id,
                "uom_type": "bigger",
                "factor_inv": 10,
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write(
            {"delivery_steps": "ship_only", "reception_steps": "one_step"}
        )

    def _new_purchase_order(self, supplier, lines_map=None):
        po_form = Form(self.env["purchase.order"])
        po_form.partner_id = supplier
        for product, values in lines_map:
            with po_form.order_line.new() as line:
                line.product_id = product
                if values.get("uom"):
                    line.product_uom = values["uom"]
                line.product_qty = values["qty"]
                line.price_unit = values["price"]
                if values.get("discount"):
                    line.discount = values["discount"]
        return po_form.save()

    def _validate_purchase_reception(self, pickings, lot=None):
        lot = lot or "001"
        for picking in pickings.filtered(lambda x: x.state not in ["done", "cancel"]):
            tracked_lines = picking.move_line_ids.filtered(
                lambda x: x.product_id.tracking == "lot"
            )
            if picking.picking_type_code == "incoming":
                tracked_lines.lot_name = lot
            else:
                for line in tracked_lines:
                    lot = self.env["stock.lot"].search(
                        [("name", "=", lot), ("product_id", "=", line.product_id.id)]
                    )
                    line.lot_id = lot
            picking.action_set_quantities_to_reservation()
            picking._action_done()

    def _partial_return(self, picking, qty):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity = qty
        stock_return_picking_action = stock_return_picking.create_returns()
        return_pick = self.env["stock.picking"].browse(
            stock_return_picking_action["res_id"]
        )
        self._validate_purchase_reception(return_pick)

    def _deliver_to_customer(self, product, qty, lot=None):
        picking_out_form = Form(self.env["stock.picking"])
        picking_out_form.picking_type_id = self.env.ref("stock.picking_type_out")
        with picking_out_form.move_ids_without_package.new() as move:
            move.product_id = product
            move.product_uom_qty = qty
        picking = picking_out_form.save()
        picking.action_confirm()
        self._validate_purchase_reception(picking, lot=lot)
        return picking

    def _valuation_layers(self, product):
        return self.env["stock.valuation.layer"].search(
            [("product_id", "=", product.id)]
        )

    def _log_svls(self, product, title=None):
        """Tool to quickly log the svls values"""
        fields = [
            "value",
            "quantity",
            "unit_cost",
            "reference",
            "remaining_value",
            "remaining_qty",
        ]
        totals = ["value", "quantity", "remaining_value", "remaining_qty"]
        layers = self._valuation_layers(product)
        layers_values = layers.read(fields)
        if not layers_values:
            return
        header = list(layers_values[0].keys())
        footer = [sum(layers.mapped(f)) if f in totals else "" for f in header]
        rows = [list(layer.values()) for layer in layers_values]
        table = [header, *rows]
        widths = [max(len(str(item)) + 3 for item in col) for col in zip(*table)]
        separator = ["─" * w for w in widths]
        table.insert(1, separator)
        table.append(separator)
        if len(rows) > 1:
            table.append(footer)
        if title:
            _logger.info(
                f"\033[1m\033[3m[{product.name} "
                f"price: {product.standard_price} value: {product.value_svl}]"
                f"\033[0m {title}\033[0m"
            )
        header = "".join(
            str(item).rjust(width) for item, width in zip(table[0], widths)
        )
        # Print in bold
        _logger.info("".join(separator))
        _logger.info(f"\033[1m{header}\033[0m")
        for row in table[1:]:
            _logger.info(
                "".join(str(item).rjust(width) for item, width in zip(row, widths))
            )

    def assertValuation(self, product, valuation, price):
        self.assertAlmostEqual(product.value_svl, valuation)
        self.assertAlmostEqual(product.standard_price, price)

    def _assert_valuation_layers_count(self, product, length):
        svls_length = self.env["stock.valuation.layer"].search_count(
            [("product_id", "=", product.id)]
        )
        self.assertEqual(svls_length, length)

    def _purchase_and_receive(self, lines_map=None, lot_name=None):
        """Automatic process of the order map"""
        # It's always a good time for peaches
        if not lines_map:
            lines_map = [(self.peach, {"price": 1.1, "qty": 100})]
        purchase_order = self._new_purchase_order(
            self.supplier_frutas_calanda, lines_map
        )
        purchase_order.button_confirm()
        self._validate_purchase_reception(purchase_order.picking_ids, lot=lot_name)
        return purchase_order

    def test_01_update_reception_cost_from_vendor_bill(self):
        """Regular Odoo behavior
        1. We'll confirm the purchase order with an initial unit price
        2. Then we receive the goods which will value those entries.
        3. And later the cost/value will be fixed from the vendor bill
        Expected result: the valuation is adjusted once the vendor bill is posted.
        """
        purchase_order = self._purchase_and_receive()
        # 5. The purchase team sets the price at last and the price difference flags are
        # raised.
        purchase_order.order_line.price_unit = 1.2
        self.assertTrue(purchase_order.valuation_differs)
        self.assertValuation(self.peach, valuation=110, price=1.1)
        self._log_svls(self.peach, title="1. Initial valuation after reception")
        # 6. The order is invoiced right on and the prices are then fixed
        purchase_order.action_create_invoice()
        purchase_order.invoice_ids.invoice_date = Date.today()
        purchase_order.invoice_ids._post()
        self.assertValuation(self.peach, valuation=120, price=1.2)
        self._log_svls(self.peach, title="2. Price unit changed in invoice")

    def test_02_update_reception_cost_from_the_purchase_line(self):
        """The main goal for this module is to be able to update the product cost
        as soon as possible, as we might not be able to have a vendor bill up until
        way after the reception. So in this case:
            1. We'll confirm the purchase order with an initial unit price
            2. Then we receive the goods which will value those entries.
            3. We'll be able to fix the product valuation before the vendor bill is
               issued.
            4. Once the vendor bill is issued there won't be any price differences to
               fix anymore.
        """
        purchase_order = self._purchase_and_receive()
        # 5. The purchase team sets the price at last and the price difference flags are
        # raised.
        self._log_svls(self.peach, title="1. Initial valuation after reception")
        purchase_order.order_line.price_unit = 1.2
        self.assertTrue(purchase_order.valuation_differs)
        self.assertValuation(self.peach, valuation=110, price=1.1)
        # 6. Now we can press the "Fix valuation" button to adjust those differences
        purchase_order.action_apply_price_difference()
        self.assertValuation(self.peach, valuation=120, price=1.2)
        self._log_svls(self.peach, title="2. Price changed and fixed in PO")
        # 7. The order is invoiced later and the valuation layers remain the same
        purchase_order.action_create_invoice()
        purchase_order.invoice_ids.invoice_date = Date.today()
        purchase_order.invoice_ids._post()
        self.assertValuation(self.peach, valuation=120, price=1.2)
        self._log_svls(self.peach, title="3. Remains the same after invoice")

    def test_03_update_reception_cost_from_the_purchase_line_and_from_invoice(self):
        """In this case we want to ensure that the core invoice valuation adjustment
        still works after the valuation was updated from the PO.
         1. We'll confirm the purchase order with an initial unit price
         2. Then we receive the goods which will value those entries.
         3. We'll be able to fix the product valuation before the vendor bill is
            issued.
         4. Once the vendor bill is issued the purchase team adds a new price
            difference that which adjust the product value as well when the bill
            is posted.
        """
        purchase_order = self._purchase_and_receive()
        # 5. The purchase team sets the price at last and the price difference flags are
        # raised.
        purchase_order.order_line.price_unit = 1.2
        self.assertTrue(purchase_order.valuation_differs)
        self.assertAlmostEqual(self.peach.standard_price, 1.1)
        self.assertValuation(self.peach, valuation=110, price=1.1)
        # 6. Now we can press the "Fix valuation" button to adjust those differences
        purchase_order.action_apply_price_difference()
        self.assertValuation(self.peach, valuation=120, price=1.2)
        # 7. The order is invoiced and later the value is fixed again
        purchase_order.action_create_invoice()
        purchase_order.invoice_ids.invoice_date = Date.today()
        purchase_order.invoice_ids.invoice_line_ids.price_unit = 1.3
        purchase_order.invoice_ids._post()
        self.assertValuation(self.peach, valuation=130, price=1.3)

    def test_04a_update_reception_cost_with_returns_from_the_invoice(self):
        """Let's do it harder. Now we'll do some extra pickings that will add new
        valuation layers to fix"""
        purchase_order = self._purchase_and_receive()
        # 5. More units are added to the purchase order. We take them in
        purchase_order.order_line.product_qty = 150
        self._validate_purchase_reception(purchase_order.picking_ids)
        self.assertValuation(self.peach, valuation=165, price=1.1)
        # 5. The purchase team sets the price at last and the price difference flags are
        # raised.
        self._partial_return(purchase_order.picking_ids[0], 10)
        self.assertFalse(purchase_order.valuation_differs)
        purchase_order.order_line.price_unit = 1
        self.assertTrue(purchase_order.valuation_differs)
        # 7. The order is invoiced later and we change the price once again
        purchase_order.action_create_invoice()
        purchase_order.invoice_ids.invoice_date = Date.today()
        purchase_order.invoice_ids.invoice_line_ids.price_unit = 1.3
        purchase_order.invoice_ids._post()
        self.assertValuation(self.peach, valuation=182, price=1.3)

    def test_04b_update_reception_cost_from_the_purchase_line(self):
        """Let's do it harder. Now we'll do some extra pickings that will add new
        valuation layers to fix"""
        purchase_order = self._purchase_and_receive()
        # 5. More units are added to the purchase order. We take them in
        purchase_order.order_line.product_qty = 150
        self._validate_purchase_reception(purchase_order.picking_ids)
        self.assertValuation(self.peach, valuation=165, price=1.1)
        # 5. The purchase team sets the price at last and the price difference flags are
        # raised.
        self._partial_return(purchase_order.picking_ids[0], 10)
        self.assertFalse(purchase_order.valuation_differs)
        # Now let's decrease the value. The valuation should change accordingly
        purchase_order.order_line.price_unit = 1
        purchase_order.action_apply_price_difference()
        self.assertValuation(self.peach, valuation=140, price=1)
        # 7. The order is invoiced later and we change the price once again
        purchase_order.action_create_invoice()
        purchase_order.invoice_ids.invoice_date = Date.today()
        purchase_order.invoice_ids.invoice_line_ids.price_unit = 1.3
        purchase_order.invoice_ids._post()
        self.assertValuation(self.peach, valuation=182, price=1.3)

    def test_05_full_history(self):
        """Even harder. A full history tracing the valuation all along"""
        # Receive 100 kg of peaches at 1.1 - Peaches value: 110
        self._purchase_and_receive()
        self.assertAlmostEqual(self.peach.value_svl, 110)
        self.assertValuation(self.peach, valuation=110, price=1.1)
        # Let's receive 100 kg more - Peachs value: 220
        purchase_2 = self._purchase_and_receive()
        self.assertValuation(self.peach, valuation=220, price=1.1)
        # Let's deliver 50 peaches
        self._deliver_to_customer(self.peach, 10)
        self.assertValuation(self.peach, valuation=209, price=1.1)
        # Our last order prices has been raised!
        # The value of the stock is now:
        #    99 (1.1 *  90) The FIFO putaway strategy discounts value from these layers
        # + 200 (2.0 * 100)
        # The AVCO price is also changed!
        purchase_2.order_line.price_unit = 2
        purchase_2.action_apply_price_difference()
        self.assertValuation(self.peach, valuation=299, price=1.57)
        purchase_2.action_create_invoice()
        purchase_2.invoice_ids.invoice_date = Date.today()
        purchase_2.invoice_ids._post()
        # The value should remain untouched after the invoice
        self.assertValuation(self.peach, valuation=299, price=1.57)

    def test_06_full_history_fix_in_invoicing(self):
        """The same as the former case, but we fix it in the invoice. The resulting
        valuation should be the same!"""
        # Receive 100 kg of peaches at 1.1 - Peaches value: 110
        self._purchase_and_receive()
        self.assertAlmostEqual(self.peach.value_svl, 110)
        self.assertValuation(self.peach, valuation=110, price=1.1)
        # Let's receive 100 kg more - Peachs value: 220
        purchase_2 = self._purchase_and_receive()
        self.assertValuation(self.peach, valuation=220, price=1.1)
        # Let's deliver 50 peaches
        self._deliver_to_customer(self.peach, 10)
        self.assertValuation(self.peach, valuation=209, price=1.1)
        purchase_2.order_line.price_unit = 2
        purchase_2.action_create_invoice()
        purchase_2.invoice_ids.invoice_date = Date.today()
        purchase_2.invoice_ids._post()
        self.assertValuation(self.peach, valuation=299, price=1.57)

    def _test_multiple_receptions_lots_and_delivers(self, uom=None):
        if not uom:
            uom = self.env.ref("uom.product_uom_kgm")
        uom_qty = partial(
            self.env.ref("uom.product_uom_kgm")._compute_quantity, to_unit=uom
        )

        def uom_price(price):
            return price * uom.factor_inv

        # 1. We order raspberries and expensive melons at this price tag
        purchase_order_1 = self._purchase_and_receive(
            lines_map=[
                (
                    self.raspberry,
                    {"price": uom_price(10), "qty": uom_qty(10), "uom": uom},
                ),
                (
                    self.crown_melon,
                    {"price": uom_price(100), "qty": uom_qty(10), "uom": uom},
                ),
            ],
            lot_name="001",
        )
        self.assertValuation(self.raspberry, valuation=100, price=10)
        self.assertValuation(self.crown_melon, valuation=1000, price=100)
        # 2. Second purchase order with different pricing
        purchase_order_2 = self._purchase_and_receive(
            lines_map=[
                (
                    self.raspberry,
                    {"price": uom_price(20), "qty": uom_qty(10), "uom": uom},
                ),
                (
                    self.crown_melon,
                    {"price": uom_price(200), "qty": uom_qty(10), "uom": uom},
                ),
            ],
            lot_name="002",
        )
        self.assertValuation(self.raspberry, valuation=300, price=15)
        self.assertValuation(self.crown_melon, valuation=3000, price=150)
        # Sell 1 unit for lot 001: the valuations is fixed
        self._deliver_to_customer(self.raspberry, 1, lot="001")
        self.assertValuation(self.raspberry, valuation=285, price=15)
        # Change the price of raspberries in the first purchase order
        purchase_order_1.order_line.filtered(
            lambda x: x.product_id == self.raspberry
        ).price_unit = uom_price(5)
        self.assertTrue(purchase_order_1.valuation_differs)
        return purchase_order_1, purchase_order_2

    def test_07_test_multiple_receptions_lots_and_delivers_fix_from_invoice(
        self, uom=None
    ):
        """Odoo standard valuation fix"""
        purchase_order_1, _po2 = self._test_multiple_receptions_lots_and_delivers(
            uom=uom
        )
        purchase_order_1.action_create_invoice()
        purchase_order_1.invoice_ids.invoice_date = Date.today()
        purchase_order_1.invoice_ids._post()
        self.assertValuation(self.raspberry, valuation=240, price=12.63)

    def test_08_test_multiple_receptions_lots_and_delivers_fix_from_purchase(
        self, uom=None
    ):
        """Odoo standard valuation fix"""
        purchase_order_1, _po2 = self._test_multiple_receptions_lots_and_delivers(
            uom=uom
        )
        purchase_order_1.action_apply_price_difference()
        self.assertValuation(self.raspberry, valuation=240, price=12.63)
        purchase_order_1.action_create_invoice()
        purchase_order_1.invoice_ids.invoice_date = Date.today()
        purchase_order_1.invoice_ids._post()
        self.assertValuation(self.raspberry, valuation=240, price=12.63)

    def test_09_test_multiple_receptions_and_delivers_uom_fix_from_invoice(self):
        """Now the same as in 07 but with different units of measure"""
        self.test_07_test_multiple_receptions_lots_and_delivers_fix_from_invoice(
            uom=self.dekakilogram
        )

    def test_10_test_multiple_receptions_and_delivers_uom_fix_from_purchase(self):
        """Now the same as in 07 but with different units of measure"""
        self.test_08_test_multiple_receptions_lots_and_delivers_fix_from_purchase(
            uom=self.dekakilogram
        )

    def test_11_discount_roundings(self):
        # TODO: From v17, `discount` is available as a core feature
        if "discount" not in self.env["purchase.order.line"]:
            _logger.info(
                "purchase_discount unavailable: skipping discount rounding tests..."
            )
            return
        self._purchase_and_receive(
            lines_map=[(self.raspberry, {"price": 3.68, "qty": 1})]
        )
        self.assertValuation(self.raspberry, valuation=3.68, price=3.68)
        self._deliver_to_customer(self.raspberry, 1)
        self.assertValuation(self.raspberry, valuation=0, price=3.68)
        purchase_order = self._purchase_and_receive(
            lines_map=[(self.raspberry, {"price": 4.90, "qty": 150, "discount": 25})]
        )
        self.assertValuation(self.raspberry, valuation=551.25, price=3.68)
        self._partial_return(purchase_order.picking_ids[0], 50)
        self.assertFalse(purchase_order.valuation_differs)
        purchase_order.order_line.write({"price_unit": 6, "discount": 0})
        self.assertTrue(purchase_order.valuation_differs)
        purchase_order.action_apply_price_difference()
        self._log_svls(self.raspberry)
        self.assertValuation(self.raspberry, valuation=600, price=6)
        purchase_order.action_create_invoice()
        purchase_order.invoice_ids.invoice_date = Date.today()
        purchase_order.invoice_ids._post()
        self.assertValuation(self.raspberry, valuation=600, price=6)
