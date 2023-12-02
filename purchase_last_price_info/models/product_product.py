# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# Copyright 2019 ForgeFlow S.L.
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    last_purchase_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="product_id",
        domain=lambda self: [
            ("state", "in", ["purchase", "done"]),
            ("company_id", "in", self.env.companies.ids),
        ],
        string="Last Purchase Order Lines",
    )
    last_purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        compute="_compute_last_purchase_line_id",
        string="Last Purchase Line",
    )
    last_purchase_price = fields.Float(
        compute="_compute_last_purchase_line_id_info",
    )
    last_purchase_date = fields.Datetime(
        compute="_compute_last_purchase_line_id_info",
    )
    last_purchase_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_last_purchase_line_id_info",
        string="Last Supplier",
    )
    last_purchase_currency_id = fields.Many2one(
        comodel_name="res.currency",
        compute="_compute_last_purchase_line_id_info",
        string="Last Purchase Currency",
    )
    show_last_purchase_price_currency = fields.Boolean(
        compute="_compute_show_last_purchase_price_currency",
    )
    last_purchase_price_currency = fields.Float(
        string="Last currency purchase price",
        compute="_compute_last_purchase_price_currency",
        digits=0,
    )

    @api.depends("last_purchase_line_ids")
    def _compute_last_purchase_line_id(self):
        for item in self:
            item.last_purchase_line_id = fields.first(item.last_purchase_line_ids)

    @api.depends("last_purchase_line_id")
    def _compute_last_purchase_line_id_info(self):
        for item in self:
            item.last_purchase_price = item.last_purchase_line_id.price_unit
            item.last_purchase_date = item.last_purchase_line_id.date_order
            item.last_purchase_supplier_id = item.last_purchase_line_id.partner_id
            item.last_purchase_currency_id = item.last_purchase_line_id.currency_id

    @api.depends("last_purchase_line_id", "last_purchase_currency_id")
    def _compute_show_last_purchase_price_currency(self):
        for item in self:
            last_line = item.last_purchase_line_id
            item.show_last_purchase_price_currency = (
                last_line
                and item.last_purchase_currency_id
                and item.last_purchase_currency_id != last_line.company_id.currency_id
            )

    @api.depends(
        "last_purchase_line_id",
        "show_last_purchase_price_currency",
        "last_purchase_currency_id",
        "last_purchase_date",
    )
    def _compute_last_purchase_price_currency(self):
        for item in self:
            if item.show_last_purchase_price_currency:
                rates = item.last_purchase_currency_id._get_rates(
                    item.last_purchase_line_id.company_id, item.last_purchase_date
                )
                item.last_purchase_price_currency = rates.get(
                    item.last_purchase_currency_id.id
                )
            else:
                item.last_purchase_price_currency = 1
