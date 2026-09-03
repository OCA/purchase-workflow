##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_round


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    package_qty = fields.Float(
        digits="Product Unit of Measure",
        help="The quantity of products in a package.",
    )
    indicative_package = fields.Boolean()
    product_qty_package = fields.Float(
        "Number of packages", help="""The number of packages you'll buy."""
    )
    price_policy = fields.Selection(
        [("uom", "per UOM"), ("package", "per Package")],
        default="uom",
    )
    unit_price = fields.Float(
        string="Price Unit",
        compute="_compute_product_prices",
        digits="Product Price",
    )
    package_price = fields.Float(
        compute="_compute_product_prices",
        digits="Product Price",
    )

    # adding price_policy to depends
    @api.depends("price_policy", "product_qty_package")
    def _compute_amount(self):
        return super()._compute_amount()

    @api.depends("package_qty", "price_unit", "price_policy")
    def _compute_product_prices(self):
        for line in self:
            if line.price_policy == "package":
                line.unit_price = (
                    line.package_qty and line.price_unit / line.package_qty or 0
                )
                line.package_price = line.price_unit
            else:
                line.unit_price = line.price_unit
                line.package_price = line.price_unit * line.package_qty

    # Constraints section
    @api.constrains("product_id", "product_qty", "indicative_package")
    def _check_purchase_qty(self):
        lines = self.filtered(
            lambda _l: (
                _l.state in ("draft", "sent")
                and _l.product_id
                and _l.package_qty > 0
                and not _l.indicative_package
            )
        )
        for pol in lines:
            if (
                int(pol.product_qty / pol.package_qty)
                != pol.product_qty / pol.package_qty
            ):
                raise ValidationError(
                    self.env._(
                        """You have to buy a multiple of the package"""
                        """ qty or change the package settings in the"""
                        """ supplierinfo of the product for the"""
                        """ following line:"""
                        """ \n - Product: %s;"""
                        """ \n - Quantity: %s;"""
                        """ \n - Unit Price: %s;"""
                        """ \n - Package quantity: %s;""",
                        pol.product_id.name,
                        pol.product_qty,
                        pol.price_unit,
                        pol.package_qty,
                    )
                )

    # Views section
    def _product_id_change(self):
        """Override to set indicative_package, and price_policy
        from the selected supplierinfo.
        """
        res = super()._product_id_change()
        if not self.product_id or self.invoice_lines or not self.company_id:
            return res
        params = self._get_select_sellers_params()
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=None,
            date=(
                self.order_id.date_order
                and self.order_id.date_order.date()
                or fields.Date.context_today(self)
            ),
            uom_id=self.product_uom,
            params=params,
        )
        if seller:
            self.package_qty = seller.package_qty
            self.indicative_package = seller.indicative_package
            self.product_qty = seller.package_qty
            self.product_qty_package = 1
            self.price_policy = seller.price_policy
        return res

    @api.depends("price_policy")
    def _compute_price_unit_and_date_planned_and_name(self):
        res = super()._compute_price_unit_and_date_planned_and_name()
        lines = self.filtered(
            lambda _l: _l.product_id
            and not _l.invoice_lines
            and _l.price_policy == "package"
        )
        lines._update_price_unit_by_package_policy()
        return res

    def _update_price_unit_by_package_policy(self):
        for line in self:
            params = line._get_select_sellers_params()
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order
                and line.order_id.date_order.date()
                or fields.Date.context_today(line),
                uom_id=line.product_uom,
                params=params,
            )

            if seller:
                seller_price = seller.base_price
                if seller.price_policy == "uom":
                    seller_price *= seller.package_qty

                price_unit = line.env["account.tax"]._fix_tax_included_price_company(
                    seller_price,
                    line.product_id.supplier_taxes_id,
                    line.taxes_id,
                    line.company_id,
                )
                price_unit = seller.currency_id._convert(
                    price_unit,
                    line.currency_id,
                    line.company_id,
                    line.date_order or fields.Date.context_today(line),
                    False,
                )
                price_unit = float_round(
                    price_unit,
                    precision_digits=max(
                        line.currency_id.decimal_places,
                        self.env["decimal.precision"].precision_get("Product Price"),
                    ),
                )
                line.price_unit = seller.product_uom._compute_price(
                    price_unit, line.product_uom
                )

    def _prepare_account_move_line(self, move=False):
        vals = super()._prepare_account_move_line(move=move)
        vals.update(
            {
                "price_policy": self.price_policy,
                "package_qty": self.package_qty,
            }
        )
        if self.package_qty and vals.get("quantity"):
            vals["product_qty_package"] = vals["quantity"] / self.package_qty
        return vals

    @api.onchange("product_qty_package")
    def onchange_product_qty_package(self):
        if (
            self.package_qty
            and self.product_qty_package == int(self.product_qty_package)
            and (
                not self.env.context.get("mail_notrack")
                or self.package_qty != 1
                or self.product_qty_package != 1
            )
        ):
            product_qty_package = self.product_qty / self.package_qty

            if round(product_qty_package, 2) != self.product_qty_package:
                self.product_qty = self.package_qty * self.product_qty_package

    @api.onchange("package_qty")
    def onchange_package_qty(self):
        if not self.package_qty:
            self.package_qty = 1
        self.product_qty = self.package_qty * self.product_qty_package

    def _prepare_stock_move_vals(
        self, picking, price_unit, product_uom_qty, product_uom
    ):
        vals = super()._prepare_stock_move_vals(
            picking, price_unit, product_uom_qty, product_uom
        )
        vals.update(
            {
                "package_qty": self.package_qty,
                "product_qty_package": self.product_qty_package,
            }
        )
        return vals
