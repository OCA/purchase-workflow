##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
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


class ComputedPurchaseOrderLine(models.Model):
    _description = "Computed Purchase Order Line"
    _name = "computed.purchase.order.line"
    _order = "sequence"

    _STATE = [
        ("new", "New"),
        ("up_to_date", "Up to date"),
        ("updated", "Updated"),
    ]

    # Columns section
    computed_purchase_order_id = fields.Many2one(
        "computed.purchase.order",
        "Order Reference",
        required=True,
        ondelete="cascade",
    )
    state = fields.Selection(
        _STATE,
        compute="_compute_state",
        store=True,
        readonly=True,
        help="Shows if the product's information has been updated",
    )
    sequence = fields.Integer(
        help="""Gives the sequence order when displaying a list of"""
        """ purchase order lines."""
    )
    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain=[("purchase_ok", "=", True)],
    )
    uom_id = fields.Many2one(related="product_id.uom_id")
    uom_po_id = fields.Many2one(
        related="product_id.uom_po_id",
    )
    psi_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        compute="_compute_psi",
        store=True,
        readonly=False,
    )
    product_sequence = fields.Integer(
        string="Product Sequence",
        related="product_id.sequence",
    )
    product_code = fields.Char(
        "Supplier Product Code",
        compute="_compute_values_from_psi",
        store=True,
        readonly=False,
    )
    product_name = fields.Char(
        "Supplier Product Name",
        compute="_compute_values_from_psi",
        store=True,
        readonly=False,
    )
    product_price = fields.Float(
        "Supplier Product Price",
        compute="_compute_product_price",
        store=True,
        readonly=False,
        digits="Product Price",
    )
    discount = fields.Float(
        compute="_compute_values_from_psi",
        store=True,
        readonly=False,
        digits="Discount",
    )
    price_policy = fields.Selection(
        [("uom", "per UOM"), ("package", "per Package")],
        compute="_compute_values_from_psi",
        store=True,
        readonly=False,
    )
    shelf_life = fields.Integer(
        string="Shelf life (days)",
        compute="_compute_values_from_psi",
        store=True,
        readonly=False,
    )

    subtotal = fields.Float(
        compute="_compute_subtotal_price",
        digits="Product Price",
    )

    package_qty = fields.Float(
        string="Package Quantity",
        compute="_compute_values_from_psi",
        store=True,
        readonly=False,
    )
    weight = fields.Float(
        related="product_id.weight",
        string="Net Weight",
    )
    average_consumption = fields.Float(
        compute="_compute_average_consumption",
        digits=(12, 3),
    )
    displayed_average_consumption = fields.Float(
        digits=(12, 3),
    )
    consumption_range = fields.Integer(
        "Range (days)",
        help="""Range (in days) used to display the average
        consumption""",
    )
    stock_duration = fields.Float(
        compute="_compute_stock_duration",
        string="Stock Duration (Days)",
        help="Number of days the stock should last.",
    )
    virtual_duration = fields.Float(
        compute="_compute_stock_duration",
        string="Virtual Duration (Days)",
        help="Number of days the stock should last after the purchase.",
    )
    purchase_qty_package = fields.Float(
        string="Number of packages",
        help="""The number of packages you'll buy.""",
    )
    purchase_qty = fields.Float(
        string="Quantity to purchase",
        compute="_compute_purchase_qty",
        readonly=False,
        store=True,
        help="The quantity you should purchase.",
    )
    manual_input_output_qty = fields.Float(
        string="Manual variation",
        default=0,
        help="""Write here some extra quantity depending of some"""
        """ input or output of products not entered in the software\n"""
        """- negative quantity : extra output ; \n"""
        """- positive quantity : extra input.""",
    )
    qty_available = fields.Float(
        compute="_compute_qty",
        string="On Hand Quantity",
        help="The available quantity on hand for this product",
    )
    incoming_qty = fields.Float(
        compute="_compute_qty",
        string="Incoming Quantity",
        help="Virtual incoming entries",
    )
    outgoing_qty = fields.Float(
        compute="_compute_qty",
        string="Outgoing Quantity",
        help="Virtual outgoing entries",
    )
    virtual_qty = fields.Float(
        compute="_compute_qty",
        string="Virtual Quantity",
        help="Quantity on hand + Virtual incoming and outgoing entries",
    )
    computed_qty = fields.Float(
        compute="_compute_computed_qty",
        string="Stock",
        help="The sum of all quantities selected.",
        digits="Product UoM",
    )
    cpo_state = fields.Selection(
        string="CPO State",
        related="computed_purchase_order_id.state",
    )

    # Constraints section
    _sql_constraints = [
        (
            "product_id_uniq",
            "unique(computed_purchase_order_id,product_id)",
            "Product must be unique by computed purchase order!",
        ),
    ]

    def _get_psi_fields_related_value(self):
        return [
            "product_code",
            "product_name",
            "discount",
            "price_policy",
            "shelf_life",
            "package_qty",
        ]

    def _get_psi_fields_sync_value(self):
        return [
            "product_code",
            "product_name",
            # "discount",  # No sync
            "price_policy",
            "shelf_life",
            "package_qty",
            "product_price",  # To consider
        ]

    @api.depends(lambda self: self._get_psi_fields_sync_value())
    def _compute_state(self):
        field_names = self._get_psi_fields_sync_value()
        if "product_price" in field_names:
            field_names.remove("product_price")
        for rec in self:
            if not rec.psi_id:
                rec.state = "new"
            else:
                is_updated = any(rec[fn] != rec.psi_id[fn] for fn in field_names)
                if not is_updated:
                    # Check price
                    is_updated = rec.product_price != rec._get_psi_price()
                rec.state = is_updated and "updated" or "up_to_date"

    @api.depends("psi_id")
    def _compute_values_from_psi(self):
        field_names = self._get_psi_fields_related_value()
        for rec in self:
            for fn in field_names:
                rec[fn] = rec.psi_id[fn] if rec.psi_id else False

    def _find_psi(self, qty=None, ordered_by="price_discounted"):
        seller = self.env["product.supplierinfo"]
        if not self.product_id:
            return seller
        cpo = self.computed_purchase_order_id
        seller = self.product_id._select_seller(
            partner_id=cpo.partner_id,
            quantity=qty,
            date=(cpo.incoming_date or fields.Date.context_today(self)),
            uom_id=self.product_id.uom_po_id,
            ordered_by=ordered_by,
        )
        return seller

    @api.depends("computed_purchase_order_id", "product_id")
    def _compute_psi(self):
        for rec in self:
            rec.psi_id = rec._find_psi()

    @api.depends("purchase_qty_package", "package_qty")
    def _compute_purchase_qty(self):
        for cpol in self:
            if (
                cpol.purchase_qty_package
                and int(cpol.purchase_qty_package) == cpol.purchase_qty_package
            ):
                cpol.purchase_qty = cpol.package_qty * cpol.purchase_qty_package
            else:
                cpol.purchase_qty = cpol.purchase_qty

    def _get_psi_price(self, psi=None):
        return self._get_psi_price_data(psi)[0]

    def _get_psi_price_field_name(self, psi=None):
        return self._get_psi_price_data(psi)[1]

    def _get_psi_price_data(self, psi=None):
        """
        Returns the price and the field name used to get the price from PSI
        """
        self.ensure_one()
        if not psi:
            psi = self.psi_id
        if not psi:
            return 0.0, "price"
        if self.price_policy == "package":
            return psi.base_price, "base_price"
        else:
            return psi.price, "price"

    @api.depends("psi_id", "price_policy")
    def _compute_product_price(self):
        for line in self:
            line.product_price = line._get_psi_price()

    @api.depends(
        "purchase_qty",
        "purchase_qty_package",
        "product_price",
        "price_policy",
    )
    def _compute_subtotal_price(self):
        for line in self:
            net_unit_price = line.product_price * (1 - line.discount / 100.0)
            if line.price_policy == "package":
                line.subtotal = line.purchase_qty_package * net_unit_price
            else:
                line.subtotal = line.purchase_qty * net_unit_price

    @api.depends("displayed_average_consumption", "consumption_range")
    def _compute_average_consumption(self):
        for line in self:
            line.average_consumption = (
                line.consumption_range
                and line.displayed_average_consumption / line.consumption_range
                or 0
            )

    # Fields Function section
    @api.depends("product_id")
    def _compute_qty(self):
        for cpol in self:
            cpol.qty_available = cpol.product_id.qty_available
            cpol.incoming_qty = cpol.product_id.incoming_qty
            cpol.outgoing_qty = cpol.product_id.outgoing_qty
            cpol.virtual_qty = (
                cpol.qty_available + cpol.incoming_qty - cpol.outgoing_qty
            )

    @api.depends(
        "qty_available", "incoming_qty", "outgoing_qty", "computed_purchase_order_id"
    )
    def _compute_computed_qty(self):
        for cpol in self:
            computed_qty = cpol.qty_available
            if cpol.computed_purchase_order_id.compute_pending_quantity:
                computed_qty += cpol.incoming_qty - cpol.outgoing_qty
            cpol.computed_qty = computed_qty

    @api.depends(
        "purchase_qty",
        "average_consumption",
        "computed_qty",
        "manual_input_output_qty",
    )
    def _compute_stock_duration(self):
        for cpol in self:
            cpol.stock_duration = 0
            cpol.virtual_duration = 0
            if cpol.product_id:
                if cpol.average_consumption != 0:
                    cpol.stock_duration = (
                        cpol.computed_qty + cpol.manual_input_output_qty
                    ) / cpol.average_consumption
                    cpol.virtual_duration = (
                        cpol.computed_qty
                        + cpol.manual_input_output_qty
                        + cpol.purchase_qty
                    ) / cpol.average_consumption

    def unlink_psi(self):
        PSI = self.env["product.supplierinfo"]
        for cpol in self:
            cpo = cpol.computed_purchase_order_id
            partner_id = cpo.partner_id.id
            product_tmpl_id = cpol.product_id.product_tmpl_id.id
            domain_psi = [
                ("partner_id", "=", partner_id),
                ("product_tmpl_id", "=", product_tmpl_id),
            ]
            psi_ids = PSI.search(domain_psi)
            psi_ids.unlink()
            cpol.unlink()

    def _get_psi_values_new(self):
        """
        Get the values (cached) to create the PSI from CPO Line
        """
        self.ensure_one()
        vals = {
            "partner_id": self.computed_purchase_order_id.partner_id,
            "product_tmpl_id": self.product_id.product_tmpl_id,
            # "min_qty": self.package_qty,
            # "discount": self.discount,
        }
        vals.update(self._get_psi_values_update())
        return vals

    def _get_psi_values_update(self):
        """
        Get the values (cached) to update the PSI from CPO Line
        """
        self.ensure_one()
        vals = {}
        field_names = self._get_psi_fields_sync_value()
        if "product_price" in field_names:
            field_names.remove("product_price")
        for fn in field_names:
            vals[fn] = self[fn]
        # Set the product_price
        vals["base_price"] = self.product_price
        return vals

    def create_psi(self):
        for line in self.filtered(lambda _l: not _l.psi_id):
            line.psi_id = self.env["product.supplierinfo"].new(
                line._get_psi_values_new()
            )

    def update_psi(self):
        for line in self.filtered(lambda _l: _l.psi_id):
            line.psi_id.update(line._get_psi_values_update())
