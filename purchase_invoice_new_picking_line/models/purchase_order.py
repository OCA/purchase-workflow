# SPDX-FileCopyrightText: 2024 Coop IT Easy
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models
from odoo.fields import Command


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_account_move_lines_from_stock_move(
        self, stock_move_id, account_move_id
    ):
        self.ensure_one()

        product_id = stock_move_id.product_id
        qty = max(stock_move_id.quantity_done, 0)
        date = fields.Date.to_date(stock_move_id.date) or fields.Date.today()
        supplierinfo = self.env["product.supplierinfo"]
        price_unit = 0.0
        if self.partner_id:
            supplierinfo = product_id._select_seller(
                partner_id=self.partner_id,
                quantity=qty,
                date=date,
                uom_id=stock_move_id.product_uom,
                params={"order_id": self},
            )
        if supplierinfo:
            price_unit = supplierinfo.currency_id._convert(
                supplierinfo.price,
                self.currency_id,
                self.company_id,
                date,
                round=False,
            )
        else:
            price_unit = product_id.currency_id._convert(
                product_id.lst_price,
                self.currency_id,
                self.company_id,
                date,
                round=False,
            )
        taxes = product_id.supplier_taxes_id.filtered(
            lambda tax: tax.company_id == self.company_id
        )
        tax_ids = self.fiscal_position_id.map_tax(taxes)  # TODO not sure about this

        data = {
            "display_type": "product",
            # Normally the name is '{order_name}: {order_line_name}'.
            "name": "%s: %s" % (stock_move_id.picking_id.name, stock_move_id.name),
            "product_id": product_id.id,
            "product_uom_id": stock_move_id.product_uom.id,
            "quantity": qty,
            "price_unit": price_unit,
            "tax_ids": [Command.set(tax_ids.ids)],
        }

        return data

    def add_missing_picking_products_to_account_move(self, account_move_id):
        stock_moves = self.env["stock.move"]
        for picking in self.picking_ids.filtered(lambda x: x.state == "done"):
            stock_moves |= picking.move_ids.filtered(
                lambda move: move.state == "done" and not move.purchase_line_id
            )
        new_lines_data = [
            self._prepare_account_move_lines_from_stock_move(
                stock_move, account_move_id
            )
            for stock_move in stock_moves
        ]
        account_move_id.write(
            {"invoice_line_ids": [Command.create(line) for line in new_lines_data]}
        )

    def action_create_invoice(self):
        result = super().action_create_invoice()
        res_id = result.get("res_id")
        if not res_id:
            return result
        invoice_id = self.env["account.move"].browse(res_id)
        self.add_missing_picking_products_to_account_move(invoice_id)
        return result
