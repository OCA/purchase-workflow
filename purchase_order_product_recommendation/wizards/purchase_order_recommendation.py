# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# Copyright 2020 Manuel Calero - Tecnativa
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderRecommendation(models.TransientModel):
    _name = "purchase.order.recommendation"
    _description = "Recommended products for current purchase order"

    order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase Order",
        default=lambda self: self._default_order_id(),
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    date_begin = fields.Date(
        default=fields.Date.context_today,
        required=True,
        help="Initial date to compute recommendations.",
    )
    date_end = fields.Date(
        default=fields.Date.context_today,
        required=True,
        help="Final date to compute recommendations.",
    )
    line_ids = fields.One2many(
        comodel_name="purchase.order.recommendation.line",
        inverse_name="wizard_id",
        string="Products",
    )
    line_amount = fields.Integer(
        string="Number of recommendations",
        default=15,
        required=True,
        help="Stablish a limit on how many recommendations you want to get."
        "Leave it as 0 to set no limit",
    )
    show_all_partner_products = fields.Boolean(
        string="Show all supplier products",
        default=False,
        help="Show all products with supplier infos for this supplier",
    )
    show_all_products = fields.Boolean(
        string="Show all purchasable products",
        default=False,
        help="Useful if a product hasn't been selled by the partner yet",
    )
    product_category_ids = fields.Many2many(
        comodel_name="product.category",
        string="Product Categories",
        help="Filter by product internal category",
    )
    warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse",
        string="Warehouse",
        help="Constrain search to an specific warehouse",
    )
    warehouse_count = fields.Integer(
        default=lambda self: len(self.env["stock.warehouse"].search([])),
    )

    @api.model
    def _default_order_id(self):
        if self.env.context.get("active_model", False) != "purchase.order":
            raise UserError(_("This wizard is only valid for purchases"))
        return self.env.context.get("active_id", False)

    def _get_total_days(self):
        """Compute days between the initial and the end date"""
        day = (self.date_end + timedelta(days=1) - self.date_begin).days
        return day

    def _get_supplier_products(self):
        """Common method to be used for field domain filters"""
        supplierinfo_obj = self.env["product.supplierinfo"].with_context(
            prefetch_fields=False
        )
        partner = self.order_id.partner_id.commercial_partner_id
        supplierinfos = supplierinfo_obj.search([("partner_id", "=", partner.id)])
        product_tmpls = supplierinfos.mapped("product_tmpl_id").filtered(
            lambda x: x.active and x.purchase_ok
        )
        products = supplierinfos.mapped("product_id").filtered(
            lambda x: x.active and x.purchase_ok
        )
        products += product_tmpls.mapped("product_variant_ids")
        return products

    def _get_products(self):
        """Override to filter products show_all_partner_products is set"""
        products = self._get_supplier_products()
        # Filter products by category if set.
        # It will apply to show_all_partner_products as well
        if self.product_category_ids:
            products = products.filtered(
                lambda x: x.categ_id in self.product_category_ids
            )
        return products

    def _get_move_line_domain(self, products, src, dst):
        """Allows to easily extend the domain by third modules"""
        combine = datetime.combine
        # We can receive a context to be able to get different dates with
        # the same wizard attributes, for example comparing periods
        date_begin = self.env.context.get("period_date_begin", self.date_begin)
        date_end = self.env.context.get("period_date_end", self.date_end)
        domain = [
            ("product_id", "in", products.ids),
            ("date", ">=", combine(date_begin, datetime.min.time())),
            ("date", "<=", combine(date_end, datetime.max.time())),
            ("location_id.usage", "=", src),
            ("location_dest_id.usage", "=", dst),
            ("state", "=", "done"),
        ]
        if self.warehouse_ids:
            domain += [
                (
                    "picking_id.picking_type_id.warehouse_id",
                    "in",
                    self.warehouse_ids.ids,
                )
            ]
        return domain

    def _get_all_products_domain(self):
        """Override to add more product filters if show_all_products is set"""
        domain = [
            ("purchase_ok", "=", True),
        ]
        if self.product_category_ids:
            domain += [("categ_id", "in", self.product_category_ids.ids)]
        return domain

    def _find_move_line(self, src="internal", dst="customer"):
        """ "Returns a dictionary from the move lines in a range of dates
        from and to given location types"""
        products = self._get_products()
        domain = self._get_move_line_domain(products, src, dst)
        found_lines = self.env["stock.move.line"].read_group(
            domain, ["product_id", "qty_done"], ["product_id"]
        )
        # Manual ordering that circumvents ORM limitations
        found_lines = sorted(
            found_lines,
            key=lambda res: (
                res["product_id_count"],
                res["qty_done"],
            ),
            reverse=True,
        )
        product_dict = {p.id: p for p in products}
        found_lines = [
            {
                "id": x["product_id"][0],
                "product_id": product_dict[x["product_id"][0]],
                "product_id_count": x["product_id_count"],
                "qty_done": x["qty_done"],
            }
            for x in found_lines
        ]
        found_lines = {line["id"]: line for line in found_lines}
        # Show every purchaseable product
        if self.show_all_products:
            products += self.env["product.product"].search(
                self._get_all_products_domain()
            )
        # Show all products with supplier infos belonging to a partner
        if self.show_all_partner_products or self.show_all_products:
            for product in products.filtered(lambda p: p.id not in found_lines.keys()):
                found_lines.update({product.id: {"product_id": product}})
        return found_lines

    def _prepare_wizard_line_from_seller(self, vals, seller):
        """Allow to add values coming from the selected seller, which will have
        more priority than existing prepared values.

        :param vals: Existing wizard line dictionary vals.
        :param seller: Selected seller for this line.
        """
        self.ensure_one()
        return {
            "price_unit": seller.price,
        }

    def _prepare_wizard_line(self, vals, order_line=False):
        """Used to create the wizard line"""
        self.ensure_one()
        product_id = order_line and order_line.product_id or vals["product_id"]
        if self.warehouse_ids:
            units_available = sum(
                product_id.with_context(warehouse=wh).qty_available
                for wh in self.warehouse_ids.ids
            )
            units_virtual_available = sum(
                product_id.with_context(warehouse=wh).virtual_available
                for wh in self.warehouse_ids.ids
            )
        else:
            units_available = product_id.qty_available
            units_virtual_available = product_id.virtual_available
        qty_to_order = abs(
            min(0, units_virtual_available - vals.get("qty_delivered", 0))
        )
        vals["is_modified"] = bool(qty_to_order)
        units_included = order_line and order_line.product_qty or qty_to_order
        seller = product_id._select_seller(
            partner_id=self.order_id.partner_id,
            date=fields.Date.today(),
            quantity=units_included,
            uom_id=product_id.uom_po_id,
        )
        res = {
            "purchase_line_id": order_line and order_line.id,
            "product_id": product_id.id,
            "product_name": product_id.name,
            "product_code": product_id.code,
            "times_delivered": vals.get("times_delivered", 0),
            "times_received": vals.get("times_received", 0),
            "units_received": vals.get("qty_received", 0),
            "units_available": units_available,
            "units_virtual_available": units_virtual_available,
            "units_avg_delivered": (
                vals.get("qty_delivered", 0) / self._get_total_days()
            ),
            "units_delivered": vals.get("qty_delivered", 0),
            "units_included": units_included,
            "is_modified": vals.get("is_modified", False),
        }
        res.update(self._prepare_wizard_line_from_seller(res, seller))
        return res

    @api.onchange(
        "order_id",
        "date_begin",
        "date_end",
        "line_amount",
        "show_all_partner_products",
        "show_all_products",
        "product_category_ids",
        "warehouse_ids",
    )
    def _generate_recommendations(self):
        """Generate lines according to received and delivered items"""
        self.line_ids = False
        # Get quantities received from suppliers
        found_dict = self._find_move_line(src="supplier", dst="internal")
        for product, line in found_dict.items():
            found_dict[product]["qty_received"] = line.get("qty_done", 0)
            found_dict[product]["times_received"] = line.get("product_id_count", 0)
        # Get quantities delivered to customers
        found_delivered_dict = self._find_move_line(src="internal", dst="customer")
        # Merge the two dicts
        for product, line in found_delivered_dict.items():
            if not found_dict.get(product):
                found_dict[product] = line
            found_dict[product]["qty_delivered"] = line.get("qty_done", 0)
            found_dict[product]["times_delivered"] = line.get("product_id_count", 0)
            found_dict[product].update(
                {k: v for k, v in line.items() if k not in found_dict[product].keys()}
            )
        RecomendationLine = self.env["purchase.order.recommendation.line"]
        existing_product_ids = []
        # Add products from purchase order lines
        for order_line in self.order_id.order_line:
            found_line = found_dict.get(order_line.product_id.id, {})
            new_line = RecomendationLine.new(
                self._prepare_wizard_line(found_line, order_line)
            )
            self.line_ids += new_line
            existing_product_ids.append(order_line.product_id.id)
        # Add those recommendations too
        i = 0
        for product, line in found_dict.items():
            if product in existing_product_ids:
                continue
            new_line = RecomendationLine.new(self._prepare_wizard_line(line))
            self.line_ids += new_line
            # Limit number of results. It has to be done here, as we need to
            # populate all results first, for being able to select best matches
            i += 1
            if i == self.line_amount:
                break
        self.line_ids = self.line_ids.sorted(key=lambda x: x.product_id.name)

    def action_accept(self):
        """Propagate recommendations to purchase order."""
        po_lines = self.env["purchase.order.line"]
        sequence = max(self.order_id.mapped("order_line.sequence") or [0])
        for wiz_line in self.line_ids.filtered("is_modified"):
            # Use preexisting line if any
            if wiz_line.purchase_line_id:
                if wiz_line.units_included:
                    wiz_line.purchase_line_id.update(wiz_line._prepare_update_po_line())
                else:
                    wiz_line.purchase_line_id.unlink()
                continue
            sequence += 1
            # Use a new in-memory line otherwise
            po_line = po_lines.new(wiz_line._prepare_new_po_line(sequence))
            po_line.onchange_product_id()
            po_line.product_qty = wiz_line.units_included
            po_lines |= po_line
        self.order_id.order_line |= po_lines


class PurchaseOrderRecommendationLine(models.TransientModel):
    _name = "purchase.order.recommendation.line"
    _description = "Recommended product for current purchase order"
    _order = "id"

    currency_id = fields.Many2one(
        related="product_id.currency_id",
        readonly=True,
    )
    partner_id = fields.Many2one(
        related="wizard_id.order_id.partner_id",
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )
    product_name = fields.Char()
    product_code = fields.Char(string="Product reference")
    price_unit = fields.Monetary(
        readonly=True,
    )
    times_delivered = fields.Integer(
        readonly=True,
    )
    times_received = fields.Integer(
        readonly=True,
    )
    units_received = fields.Float(
        readonly=True,
    )
    units_delivered = fields.Float(
        readonly=True,
    )
    units_avg_delivered = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
    )
    units_available = fields.Float(
        readonly=True,
    )
    units_virtual_available = fields.Float(
        readonly=True,
    )
    units_included = fields.Float()
    wizard_id = fields.Many2one(
        comodel_name="purchase.order.recommendation",
        string="Wizard",
        ondelete="cascade",
        required=True,
        readonly=True,
    )
    purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
    )
    is_modified = fields.Boolean()

    @api.onchange("units_included")
    def _onchange_units_included(self):
        self.is_modified = bool(self.purchase_line_id or self.units_included)
        self.price_unit = self.product_id._select_seller(
            partner_id=self.partner_id,
            date=fields.Date.today(),
            quantity=self.units_included,
            uom_id=self.product_id.uom_po_id,
        ).price

    def _prepare_update_po_line(self):
        """So we can extend PO update"""
        return {
            "product_qty": self.units_included,
        }

    def _prepare_new_po_line(self, sequence):
        """So we can extend PO create"""
        return {
            "order_id": self.wizard_id.order_id.id,
            "product_id": self.product_id.id,
            "sequence": sequence,
        }
