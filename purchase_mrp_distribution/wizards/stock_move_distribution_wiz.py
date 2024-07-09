# Copyright 2024 Tecnativa - Carlos Roca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


# TODO: Revisar si se crean las svls correctamente
class AccountSaleStockReportNonBilledWiz(models.TransientModel):
    _name = "stock.move.distribution.wiz"
    _description = "Wizard to distribute product qty to diferent products"

    @api.model
    def default_get(self, fields):
        ctx = self.env.context.copy()
        res = super().default_get(fields)
        if ctx.get("active_id") and ctx.get("active_model") == "stock.move":
            move = self.env["stock.move"].browse(ctx["active_id"])
            res.update(
                {
                    "move_id": move.id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": bom_line.product_id.id,
                                "quantity": sum(
                                    move.move_line_ids.filtered(
                                        lambda ml, bl=bom_line: ml.product_id
                                        == bl.product_id
                                    ).mapped("qty_done")
                                ),
                                "uom_id": bom_line.product_uom_id.id,
                            },
                        )
                        for bom_line in move.distribution_bom_id.bom_line_ids
                    ],
                }
            )
        return res

    move_id = fields.Many2one("stock.move")
    line_ids = fields.One2many("stock.move.distribution.wiz.line", "wizard_id")
    demand_quantity = fields.Float(related="move_id.product_uom_qty")
    move_uom_id = fields.Many2one(related="move_id.product_uom")

    def button_distribute_qty(self):
        self.ensure_one()
        # Clean actual move lines
        self.move_id.move_line_ids.sudo().unlink()
        for line in self.line_ids:
            # Create new move_lines
            if line.quantity:
                self.env["stock.move.line"].create(
                    {
                        "move_id": self.move_id.id,
                        "product_id": line.product_id.id,
                        "qty_done": line.quantity,
                        "product_uom_id": line.uom_id.id,
                        "location_id": self.move_id.location_id.id,
                        "location_dest_id": self.move_id.location_dest_id.id,
                        "picking_id": self.move_id.picking_id.id,
                        "company_id": self.move_id.company_id.id,
                    }
                )
        if self.move_id.move_line_ids:
            self.move_id.state = "assigned"


class StockMoveDistributionWizLine(models.TransientModel):
    _name = "stock.move.distribution.wiz.line"
    _description = "Lines of wizard to distribute product qty to diferent products"

    wizard_id = fields.Many2one("stock.move.distribution.wiz")
    product_id = fields.Many2one("product.product")
    quantity = fields.Float(digits="Product Unit of Measure")
    uom_id = fields.Many2one("uom.uom")
