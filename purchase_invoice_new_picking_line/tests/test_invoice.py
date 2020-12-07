# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import tests
from odoo.tests.common import Form


class TestAccountInvoice(tests.common.TransactionCase):
    def test_move_line_product_is_added_to_invoice(self):
        purchase_order = self.browse_ref("purchase.purchase_order_4")
        product = self.browse_ref("product.product_product_1")
        supplier_loc = self.env.ref("stock.stock_location_suppliers")
        stock_loc = self.env.ref("stock.warehouse0").lot_stock_id

        # Confirm order
        purchase_order.button_confirm()
        picking = purchase_order.picking_ids
        moves = picking.move_ids_without_package
        self.assertEquals(len(purchase_order.order_line), len(moves))

        moves[0].quantity_done = moves[0].product_qty
        moves[1].quantity_done = moves[1].product_qty
        moves[2].quantity_done = moves[2].product_qty - 1

        new_move = self.env["stock.move"].create(
            {
                "picking_id": picking.id,
                "name": product.name,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "quantity_done": 20,
                "location_id": supplier_loc.id,
                "location_dest_id": stock_loc.id,
            }
        )

        wizard = picking.button_validate()
        backorder_confirmation = self.env[wizard["res_model"]].browse(
            wizard["res_id"]
        )
        backorder_confirmation.process_cancel_backorder()

        res = purchase_order.with_context(
            create_bill=True
        ).action_view_invoice()
        ctx = res.get("context")
        f = Form(
            self.env["account.invoice"].with_context(ctx),
            view="account.invoice_supplier_form",
        )
        invoice = f.save()

        self.assertRecordValues(
            invoice.invoice_line_ids,
            [
                {
                    "product_id": moves[0].product_id.id,
                    "quantity": moves[0].quantity_done,
                },
                {
                    "product_id": moves[1].product_id.id,
                    "quantity": moves[1].quantity_done,
                },
                {
                    "product_id": moves[2].product_id.id,
                    "quantity": moves[2].quantity_done,
                },
                {
                    "product_id": new_move.product_id.id,
                    "quantity": new_move.quantity_done,
                },
            ],
        )
