# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime

from odoo import fields, tests


class TestAccountInvoice(tests.common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.purchase_order = cls.env.ref("purchase.purchase_order_4")
        cls.product = cls.env.ref("product.product_product_1")
        cls.supplier_loc = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_loc = cls.env.ref("stock.warehouse0").lot_stock_id

        # Confirm order
        cls.purchase_order.button_confirm()
        cls.picking = cls.purchase_order.picking_ids
        cls.moves = cls.picking.move_ids

        cls.moves[0].quantity_done = cls.moves[0].product_qty
        cls.moves[1].quantity_done = cls.moves[1].product_qty
        cls.moves[2].quantity_done = cls.moves[2].product_qty - 1

    def _validate_picking(self):
        wizard = self.picking.button_validate()
        backorder_confirmation = (
            self.env[wizard["res_model"]].with_context(**wizard["context"]).create({})
        )
        backorder_confirmation.process_cancel_backorder()

    def _create_invoice(self):
        res = self.purchase_order.action_create_invoice()
        return self.env["account.move"].browse(res["res_id"])

    def test_move_line_product_is_added_to_invoice(self):
        new_move = self.env["stock.move"].create(
            {
                "picking_id": self.picking.id,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "quantity_done": 20,
                "location_id": self.supplier_loc.id,
                "location_dest_id": self.stock_loc.id,
            }
        )
        self._validate_picking()

        invoice = self._create_invoice()

        self.assertRecordValues(
            invoice.invoice_line_ids,
            [
                {
                    "product_id": self.moves[0].product_id.id,
                    "quantity": self.moves[0].quantity_done,
                },
                {
                    "product_id": self.moves[1].product_id.id,
                    "quantity": self.moves[1].quantity_done,
                },
                {
                    "product_id": self.moves[2].product_id.id,
                    "quantity": self.moves[2].quantity_done,
                },
                {
                    "product_id": new_move.product_id.id,
                    "quantity": new_move.quantity_done,
                    "price_unit": self.product.lst_price,
                    "product_uom_id": new_move.product_uom.id,
                    "display_type": "product",
                },
            ],
        )

    def test_with_supplierinfo(self):
        """Same test, but the price is now defined on supplierinfo instead of on
        the product.
        """
        self.env["product.supplierinfo"].create(
            {
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "partner_id": self.purchase_order.partner_id.id,
                "price": 1,
                "currency_id": self.purchase_order.currency_id.id,
                "date_start": fields.Date.today() - datetime.timedelta(days=90),
                "date_end": fields.Date.today() + datetime.timedelta(days=90),
            }
        )
        new_move = self.env["stock.move"].create(
            {
                "picking_id": self.picking.id,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "quantity_done": 20,
                "location_id": self.supplier_loc.id,
                "location_dest_id": self.stock_loc.id,
            }
        )
        self._validate_picking()

        invoice = self._create_invoice()

        self.assertRecordValues(
            invoice.invoice_line_ids[-1],
            [
                {
                    "product_id": new_move.product_id.id,
                    "quantity": new_move.quantity_done,
                    "price_unit": 1,
                    "product_uom_id": new_move.product_uom.id,
                    "display_type": "product",
                },
            ],
        )
