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


class StockMove(models.Model):
    _inherit = "stock.move"

    package_qty = fields.Float(
        compute="_compute_package_qty",
        help="""The quantity of products in the supplier package.""",
    )
    indicative_package = fields.Boolean()
    product_qty_package = fields.Float(
        "Number of packages", help="""The number of packages you'll buy."""
    )
    qty_done_package = fields.Float(
        "Done (package)",
        help="""The number of packages you've received.""",
        digits="Product Unit of Measure",
    )

    @api.depends("product_id")
    def _compute_package_qty(self):
        for move in self:
            package_qty = 0.0
            if move.product_id and move.picking_id:
                supplier = move.product_id._select_seller(
                    partner_id=move.picking_id.partner_id, quantity=1
                )
                if supplier:
                    # Get the first one
                    package_qty = supplier.package_qty
            move.package_qty = package_qty

    # Views section
    @api.onchange("product_id", "picking_type_id")
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        if self.product_id and self.product_id.seller_ids:
            supplier = self.product_id._select_seller(
                partner_id=self.picking_id.partner_id, quantity=1
            )
            if supplier:
                self.package_qty = supplier.package_qty
                self.product_qty = supplier.package_qty
                self.product_qty_package = 0.0
                self.indicative_package = supplier.indicative_package
        return res

    @api.onchange("product_id", "product_qty", "product_uom")
    def _onchange_suggest_packaging(self):
        res = super()._onchange_suggest_packaging()
        if self.package_qty:
            self.product_qty_package = self.product_qty / self.package_qty
        return res

    @api.onchange("product_qty_package", "package_qty")
    def onchange_product_qty_package(self):
        if self.product_qty_package == int(self.product_qty_package):
            self.product_uom_qty = self.package_qty * self.product_qty_package

    @api.onchange("quantity")
    def onchange_quantity(self):
        if self.package_qty:
            self.qty_done_package = self.quantity / self.package_qty

    @api.onchange("qty_done_package")
    def onchange_qty_done_package(self):
        if self.qty_done_package == int(self.qty_done_package):
            self.quantity = self.package_qty * self.qty_done_package

    @api.onchange("product_uom_qty")
    def onchange_product_uom_qty(self):
        if self.product_uom_qty and self.package_qty:
            self.product_qty_package = self.product_uom_qty / self.package_qty
        else:
            self.product_qty_package = 0.0

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder)
        for move in self:
            if move.purchase_line_id and move.quantity > 0 and move.package_qty:
                move.qty_done_package = move.quantity / move.package_qty
        return res
