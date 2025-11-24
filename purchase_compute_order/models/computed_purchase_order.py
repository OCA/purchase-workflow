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
from odoo.exceptions import ValidationError
from odoo.tools import float_round


class ComputedPurchaseOrder(models.Model):
    _description = "Computed Purchase Order"
    _name = "computed.purchase.order"
    _order = "id desc"

    # Constant Values
    _DEFAULT_NAME = "New"

    _STATE = [
        ("draft", "Draft"),
        ("done", "Done"),
        ("canceled", "Canceled"),
    ]

    _TARGET_TYPE = [
        ("product_price_inv_eq", "€"),
        ("time", "days"),
        ("weight", "kg"),
    ]

    _VALID_PSI = [
        ("first", "Consider only the first supplier on the product"),
        ("all", "Consider all the suppliers registered on the product"),
    ]

    # Columns section
    name = fields.Char(
        "Computed Purchase Order Reference",
        size=64,
        required=True,
        readonly=True,
        default=_DEFAULT_NAME,
        help="""Unique number of the automated purchase order, computed"""
        """ automatically when the computed purchase order is created.""",
    )
    company_id = fields.Many2one(
        "res.company",
        readonly=True,
        required=True,
        help="""When you will validate this item, this will create a"""
        """ purchase order for this company.""",
        default=lambda self: self.env.user.company_id,
    )
    active = fields.Boolean(
        default=True,
        help="""By unchecking the active field, you may hide this item"""
        """ without deleting it.""",
    )
    state = fields.Selection(_STATE, required=True, default="draft")
    incoming_date = fields.Date(
        "Wished Incoming Date", help="Wished date for products delivery."
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Supplier",
        required=True,
        domain=[("supplier_rank", ">", 0)],
        help="Supplier of the purchase order.",
    )
    line_ids = fields.One2many(
        comodel_name="computed.purchase.order.line",
        inverse_name="computed_purchase_order_id",
        string="Order Lines",
        help="Products to order.",
    )
    line_updated_ids = fields.One2many(
        comodel_name="computed.purchase.order.line",
        inverse_name="computed_purchase_order_id",
        domain=[("state", "=", "updated")],
    )
    # this is to be able to display the line_ids on 2 tabs of the view
    stock_line_ids = fields.One2many(
        compute="_compute_stock_line_ids",
        comodel_name="computed.purchase.order.line",
        inverse_name="computed_purchase_order_id",
        help="Products to order.",
    )
    compute_pending_quantity = fields.Boolean(
        "Pending quantity taken in account", default=True
    )
    purchase_order_id = fields.Many2one("purchase.order", readonly=True)
    purchase_target = fields.Integer(default=0)
    target_type = fields.Selection(
        _TARGET_TYPE,
        required=True,
        default="product_price_inv_eq",
        help="""This defines the amount of products you want to"""
        """ purchase. \n"""
        """The system will compute a purchase order based on the stock"""
        """ you have and the average consumption of each product."""
        """ * Target type '€': computed purchase order will cost at"""
        """ least the amount specified\n"""
        """ * Target type 'days': computed purchase order will last"""
        """ at least the number of days specified (according to current"""
        """ average consumption)\n"""
        """ * Target type 'kg': computed purchase order will weight at"""
        """ least the weight specified""",
    )
    line_order_field = fields.Selection(
        string="Lines Order",
        help="The field used to sort the CPO lines",
        related="partner_id.cpo_line_order_field",
    )
    line_order = fields.Selection(
        string="Lines Order Direction",
        related="partner_id.cpo_line_order",
    )
    valid_psi = fields.Selection(
        _VALID_PSI,
        "Supplier choice",
        required=True,
        default="first",
        help="""Method of selection of suppliers""",
    )
    computed_amount = fields.Float(
        compute="_compute_computed_amount_duration",
        digits="Product Price",
        string="Amount of the computed order",
    )
    package_qty_count = fields.Float(
        string="Total Quantity of Packages",
        help="Total count of packages by the current vendor",
        compute="_compute_package_quantity_count",
        readonly=True,
    )
    computed_duration = fields.Integer(
        compute="_compute_computed_amount_duration",
        string="Minimum duration after order",
    )
    products_updated = fields.Boolean(
        compute="_compute_products_updated",
        string="Indicate if there were any products updated in the list",
    )
    lines_with_qty_count = fields.Integer(
        "Total Ordered Lines",
        compute="_compute_lines_with_qty",
    )

    def onchange(self, values, field_name, field_onchange):
        # we don't need to recompute the whole CPO after changing a line
        if field_name == "line_ids":
            return {}
        return super().onchange(
            values,
            field_name,
            field_onchange,
        )

    @api.depends("line_ids")
    def _compute_stock_line_ids(self):
        for spo in self:
            spo.stock_line_ids = spo.line_ids

    @api.depends("line_ids")
    def _compute_computed_amount_duration(self):
        for cpo in self:
            min_duration = 999
            amount = 0
            for line in cpo.line_ids:
                if line.average_consumption != 0:
                    duration = (
                        line.computed_qty + line.purchase_qty
                    ) / line.average_consumption
                    min_duration = min(duration, min_duration)
                amount += line.subtotal
            cpo.computed_amount = amount
            cpo.computed_duration = min_duration

    @api.depends("line_ids.state")
    def _compute_products_updated(self):
        for cpo in self:
            updated = False
            for line in cpo.line_ids:
                if line.state == "updated":
                    updated = True
                    break
            cpo.products_updated = updated

    @api.depends("line_ids.purchase_qty")
    def _compute_lines_with_qty(self):
        for cpo in self:
            cpo.lines_with_qty_count = len(
                cpo.line_ids.filtered(lambda line: line.purchase_qty > 0)
            )

    # View Section
    @api.onchange("partner_id")
    def onchange_partner_id(self):
        # TODO: create a wizard to validate the change
        self.purchase_target = 0
        self.target_type = "product_price_inv_eq"
        if self.partner_id:
            self.purchase_target = self.partner_id.purchase_target
            self.target_type = self.partner_id.target_type
        self.line_ids = [(2, x.id, False) for x in self.line_ids]

    # Overload Section
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", self._DEFAULT_NAME) == self._DEFAULT_NAME:
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("computed.purchase.order")
                    or "/"
                )
        return super().create(vals_list)

    def write(self, vals):
        cpo_id = super().write(vals)
        if self.update_sorting(vals) or "partner_id" in vals:
            self.sort_lines()
        return cpo_id

    def _get_line_sort_key(self, psi, product):
        self.ensure_one()
        return {
            "product_code": psi.product_code or "",
            "product_name": psi.product_name or "",
            "product_sequence": product.sequence or 0,
        }[self.line_order_field or "product_code"]

    def sort_lines(self):
        for rec in self:
            lines = rec.line_ids.sorted(
                key=lambda line: rec._get_line_sort_key(line.psi_id, line.product_id),
                reverse=(rec.line_order == "desc"),
            )
            for i, line in enumerate(lines):
                line.sequence = i

    @api.model
    def update_sorting(self, vals):
        try:
            line_ids = vals.get("line_ids", False)
            if not line_ids:
                return False
            # this context check will allow you to change the field list
            # without overriding the whole function
            need_sorting_fields = self.env.context.get("need_sorting_fields", False)
            if not need_sorting_fields:
                need_sorting_fields = [
                    "average_consumption",
                    "computed_qty",
                    "stock_duration",
                    "manual_input_output_qty",
                    "product_id",
                ]
            for value in line_ids:
                if (
                    len(value) > 2
                    and value[2]
                    and isinstance(value[2], dict)
                    and (set(need_sorting_fields) & set(value[2].keys()))
                ):
                    return True
            return False
        except Exception:
            return False

    # Private Section
    def _sort_lines(self):
        cpol_obj = self.env["computed.purchase.order.line"]
        for cpo in self:
            lines = cpol_obj.browse([x.id for x in cpo.line_ids]).read(
                ["stock_duration", "average_consumption"]
            )
            lines = sorted(
                lines, key=lambda line: line["average_consumption"], reverse=True
            )
            lines = sorted(lines, key=lambda line: line["stock_duration"])

            id_index_list = {}
            for i in lines:
                id_index_list[i["id"]] = lines.index(i)
            for line_id in list(id_index_list.keys()):
                cpol_obj.browse(line_id).write({"sequence": id_index_list[line_id]})

    @api.model
    def _make_po_lines(self):
        all_lines = []
        for line in self.line_ids:
            if line.purchase_qty != 0:
                line_name = (
                    ""
                    f"{line.product_code and '[' + line.product_code + ']' or ''} "
                    f"{line.product_name or line.product_id.name}"
                )
                line_values = {
                    "name": line_name,
                    "product_qty": line.purchase_qty,
                    "price_policy": line.price_policy,
                    "package_qty": line.package_qty,
                    "product_qty_package": line.purchase_qty_package,
                    "date_planned": (
                        self.incoming_date or fields.Date.context_today(self)
                    ),
                    "product_id": line.product_id.id,
                    "price_unit": line.product_price,
                    "discount": line.discount,
                }
                all_lines.append(
                    (0, 0, line_values),
                )
        return all_lines

    def parse_qty(self, cpo_line, days):
        quantity = 0
        if cpo_line.average_consumption:
            quantity = max(
                days
                * cpo_line.average_consumption
                * cpo_line.uom_po_id.factor
                / cpo_line.uom_id.factor
                - cpo_line.computed_qty,
                0,
            )
        elif cpo_line.computed_qty == 0:
            quantity = cpo_line.package_qty
        product_price = cpo_line.product_price
        package_qty = cpo_line.package_qty

        psi = cpo_line.psi_id
        if psi:
            product_price = cpo_line._get_psi_price(psi)
            package_qty = psi.package_qty
            quantity = psi._convert_qty(quantity)
        return quantity, product_price, psi, package_qty

    def _compute_purchase_quantities_days(self):
        for cpo in self:
            days = cpo.purchase_target
            for line in cpo.line_ids:
                line = line.with_context(update_price=True)
                quantity, product_price, psi, package_qty = self.parse_qty(line, days)
                cpo._update_compute_purchase_qty(
                    line, quantity, product_price, psi, package_qty
                )

    def _update_compute_purchase_qty(
        self, line, quantity, product_price, psi, package_qty
    ):
        # Update line values after computing the purchase qty
        vals = {
            "psi_id": psi,
            "purchase_qty": quantity,
            "product_price": product_price,
            "purchase_qty_package": (package_qty and (quantity / package_qty) or 0),
        }
        # Update only changed values to avoid unnecessary updates
        for k, v in vals.items():
            if line[k] != v:
                line[k] = v

    @api.depends("line_ids.purchase_qty_package")
    def _compute_package_quantity_count(self):
        for rec in self:
            rec.package_qty_count = sum(rec.mapped("line_ids.purchase_qty_package"))

    def _update_field_list_dict_price(self, field_list_dict, line, line_qty_tmp):
        product_price_eq = 0
        quantity, product_price, psi, package_qty = line_qty_tmp
        if line.price_policy == "package":
            if package_qty:
                product_price_eq = product_price / package_qty
        else:
            product_price_eq = product_price
        field_list_dict[line.id] = product_price_eq

    def _compute_purchase_quantities_other(self, field):
        for cpo in self:
            cpol_obj = self.env["computed.purchase.order.line"]
            if not cpo.line_ids:
                return False
            target = cpo.purchase_target
            ok = False
            days = -1
            field_list = cpol_obj.browse([x.id for x in cpo.line_ids]).read([field])
            field_list_dict = {}
            for i in field_list:
                field_list_dict[i["id"]] = i[field]

            last_total_qty = 0
            same_qty = 0
            while not ok:
                days += 1
                qty_tmp = {}
                qty_tmp_tocheck = {}
                total_qty = 0
                for line in cpo.line_ids:
                    qty_tmp[line.id] = self.parse_qty(line, days)
                    qty_tmp_tocheck[line.id] = qty_tmp[line.id][0]
                    total_qty += qty_tmp[line.id][0]
                    if field == "product_price":
                        self._update_field_list_dict_price(
                            field_list_dict, line, qty_tmp[line.id]
                        )
                if last_total_qty and last_total_qty >= total_qty:
                    # This break condition helps to avoid looping
                    same_qty += 1
                    if same_qty > 100:
                        break
                else:
                    same_qty = 0
                ok = cpo._check_purchase_qty(target, field_list_dict, qty_tmp_tocheck)
                last_total_qty = total_qty

            for line in cpo.line_ids:
                quantity, product_price, psi, package_qty = qty_tmp[line.id]
                if package_qty:
                    # Package quantity must always be an integer: round it
                    # down so the ordered quantity matches whole packages.
                    nb_package = float_round(
                        quantity / package_qty,
                        precision_digits=0,
                        rounding_method="DOWN",
                    )
                    quantity = nb_package * package_qty
                cpo._update_compute_purchase_qty(
                    line, quantity, product_price, psi, package_qty
                )

    @api.model
    def _check_purchase_qty(self, target=0, field_list=None, qty_tmp=None):
        if not target or field_list is None or qty_tmp is None:
            return True

        total = 0
        for key in list(field_list.keys()):
            total += field_list[key] * qty_tmp[key]
            if total <= 0 and qty_tmp[key] > 0:
                # in case product's weight is 0
                return True
        return total >= target

    def get_psi_domain(self):
        self.ensure_one()
        args = [("partner_id", "=", self.partner_id.id)]
        return args

    def parse_cpol_vals(self, psi, product):
        res = {
            "product_id": product.id,
            "displayed_average_consumption": product.displayed_average_consumption,
            "consumption_range": product.display_range,
            "psi_id": psi.id,
        }
        return res

    # Action section
    def compute_active_product_stock(self):
        psi_obj = self.env["product.supplierinfo"]
        for cpo in self:
            pairs = []
            # TMP delete all rows,
            # TODO : depends on further request to avoid user data to be lost
            cpo.line_ids.unlink()

            # Get product_product and compute stock
            for psi in psi_obj.search(cpo.get_psi_domain()):
                for pp in psi.product_tmpl_id.filtered(
                    "purchase_ok"
                ).product_variant_ids:
                    valid_psi = pp._valid_psi(cpo.valid_psi)
                    if valid_psi and psi in valid_psi[0]:
                        pairs.append((psi, pp))

            # Sort before creating the lines so the created order (and the
            # sequence we set below) already matches the vendor's preference.
            pairs.sort(
                key=lambda p: cpo._get_line_sort_key(*p),
                reverse=(cpo.line_order == "desc"),
            )

            # update line_ids
            cpo.line_ids = [
                (0, 0, dict(cpo.parse_cpol_vals(psi, pp), sequence=i))
                for i, (psi, pp) in enumerate(pairs)
            ]

    def _get_field_from_target_type(self):
        self.ensure_one()
        mapping = {
            "product_price_inv_eq": "product_price",
            "weight": "weight",
        }
        return mapping.get(self.target_type)

    def compute_purchase_quantities(self):
        for cpo in self:
            if any([line.average_consumption for line in cpo.line_ids]):
                if cpo.target_type == "time":
                    return cpo._compute_purchase_quantities_days()
                else:
                    target_field = cpo._get_field_from_target_type()
                    if target_field:
                        return cpo._compute_purchase_quantities_other(
                            field=target_field
                        )

    def _get_purchase_order_vals(self):
        self.ensure_one()
        po_lines = self._make_po_lines()
        po_values = {
            "origin": self.name,
            "partner_id": self.partner_id.id,
            "date_planned": (self.incoming_date or fields.Date.context_today(self)),
            "order_line": po_lines,
        }
        return po_values

    def _set_done(self):
        self.ensure_one()
        self.state = "done"

    def make_order(self):
        purchase_orders = PurchaseOrder = self.env["purchase.order"]
        for cpo in self:
            purchase_values = cpo._get_purchase_order_vals()
            if not purchase_values.get("order_line"):
                raise ValidationError(
                    self.env._("All purchase quantities are set to 0!")
                )
            purchase_order = PurchaseOrder.create(purchase_values)
            purchase_orders |= purchase_order
            cpo.purchase_order_id = purchase_order
            cpo._set_done()
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        if len(purchase_orders) == 1:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = purchase_orders.id
        else:
            action["domain"] = [("id", "in", purchase_orders.ids)]
        return action

    def action_view_order_lines(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "purchase_compute_order.action_computed_purchase_order_tree"
        )
        action["domain"] = [("computed_purchase_order_id", "=", self.id)]
        action["context"] = {"search_default_ordered_products": 1}
        return action

    def open_update_products(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "purchase_compute_order.action_view_update_products"
        )
        action["res_id"] = self.id
        return action

    def btn_update_products(self):
        lines = self.mapped("line_ids").filtered(lambda _l: _l.state == "updated")
        lines.update_psi()
