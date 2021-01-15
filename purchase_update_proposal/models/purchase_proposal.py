# -*- coding: utf-8 -*-
# © 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models
import openerp.addons.decimal_precision as dp


class PurchaseLineProposal(models.Model):
    _name = "purchase.line.proposal"
    _description = "Modification proposal on quantity, date, ..."

    line_id_ = fields.Integer(compute="_compute_line_id")
    line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Purchase Line",
        required=True,
        ondelete="cascade",
    )
    order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(related="line_id.product_id", readonly=True)
    product_qty = fields.Float(
        string="Old Qty", related="line_id.product_qty", readonly=True
    )
    price_unit = fields.Float(
        string="Old Price", related="line_id.price_unit", readonly=True
    )
    date_planned = fields.Date(
        string="Old Date", related="line_id.date_planned", readonly=True
    )
    qty = fields.Float(
        string="New Qty", digits_compute=dp.get_precision("Product Unit of Measure")
    )
    date = fields.Date(string="New Date")
    price_u = fields.Float(
        string="New Price U.", digits_compute=dp.get_precision("Product Price")
    )

    def _compute_line_id(self):
        for rec in self:
            rec.line_id_ = rec.line_id.id
