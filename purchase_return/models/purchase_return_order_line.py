# Copyright 2004-2021 Odoo S.A.
# Copyright 2021 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, get_lang
from odoo.tools.float_utils import float_compare, float_round


class PurchaseReturnOrderLine(models.Model):
    _name = "purchase.return.order.line"
    _description = "Purchase Return Order Line"
    _order = "order_id, sequence, id"

    name = fields.Text(
        string="Description",
        required=True,
        compute="_compute_price_unit_and_date_planned_and_name",
        store=True,
        readonly=False,
    )
    sequence = fields.Integer(default=10)
    product_qty = fields.Float(
        string="Quantity",
        digits="Product Unit of Measure",
        required=True,
        compute="_compute_product_qty",
        store=True,
        readonly=False,
    )
    product_uom_qty = fields.Float(
        string="Total Quantity", compute="_compute_product_uom_qty", store=True
    )
    date_planned = fields.Datetime(
        string="Expected Arrival",
        index=True,
        compute="_compute_price_unit_and_date_planned_and_name",
        readonly=False,
        store=True,
        help="Delivery date expected from vendor. This date respectively defaults to "
        "vendor pricelist lead time then today's date.",
    )
    taxes_id = fields.Many2many(
        "account.tax", string="Taxes", context={"active_test": False}
    )
    product_uom = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]",
        ondelete="restrict",
    )
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain=[("purchase_ok", "=", True)],
        change_default=True,
        index="btree_not_null",
        ondelete="restrict",
    )
    product_type = fields.Selection(related="product_id.type")
    price_unit = fields.Float(
        string="Unit Price",
        required=True,
        digits="Product Price",
        aggregator="avg",
        compute="_compute_price_unit_and_date_planned_and_name",
        readonly=False,
        store=True,
    )

    price_subtotal = fields.Monetary(
        compute="_compute_amount", string="Subtotal", aggregator=None, store=True
    )
    price_total = fields.Monetary(compute="_compute_amount", string="Total", store=True)
    price_tax = fields.Float(compute="_compute_amount", string="Tax", store=True)
    order_id = fields.Many2one(
        "purchase.return.order",
        string="Order Reference",
        index=True,
        required=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        "res.company", related="order_id.company_id", string="Company", store=True
    )
    state = fields.Selection(related="order_id.state", store=True)
    invoice_lines = fields.One2many(
        "account.move.line",
        "purchase_return_line_id",
        string="Bill Lines",
        copy=False,
    )
    # Replace by invoiced Qty
    qty_invoiced = fields.Float(
        compute="_compute_qty_invoiced",
        string="Refunded Qty",
        digits="Product Unit of Measure",
        store=True,
    )
    refund_only = fields.Boolean(string="Refund only")
    qty_to_invoice = fields.Float(
        compute="_compute_qty_invoiced",
        string="To Invoice Quantity",
        store=True,
        digits="Product Unit of Measure",
    )

    partner_id = fields.Many2one(
        "res.partner",
        related="order_id.partner_id",
        string="Partner",
        store=True,
    )
    currency_id = fields.Many2one(
        related="order_id.currency_id", store=True, string="Currency"
    )
    date_order = fields.Datetime(related="order_id.date_order", string="Order Date")
    product_packaging_id = fields.Many2one(
        "product.packaging",
        string="Packaging",
        domain="[('purchase', '=', True), ('product_id', '=', product_id)]",
        check_company=True,
        compute="_compute_product_packaging_id",
        store=True,
        readonly=False,
    )
    product_packaging_qty = fields.Float(
        "Packaging Quantity",
        compute="_compute_product_packaging_qty",
        store=True,
        readonly=False,
    )
    tax_calculation_rounding_method = fields.Selection(
        related="company_id.tax_calculation_rounding_method",
        string="Tax calculation rounding method",
        readonly=True,
    )
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )

    _sql_constraints = [
        (
            "accountable_required_fields",
            "CHECK(display_type IS NOT NULL OR (product_id IS NOT NULL "
            "AND product_uom IS NOT NULL AND date_planned IS NOT NULL))",
            "Missing required fields on accountable purchase return order line.",
        ),
        (
            "non_accountable_null_fields",
            "CHECK(display_type IS NULL OR (product_id IS NULL "
            "AND price_unit = 0 AND product_uom_qty = 0 AND product_uom "
            "IS NULL AND date_planned is NULL))",
            "Forbidden values on non-accountable purchase return order line",
        ),
    ]

    @api.depends("product_qty", "price_unit", "taxes_id")
    def _compute_amount(self):
        for line in self:
            base_line = line._prepare_base_line_for_taxes_computation()
            self.env["account.tax"]._add_tax_details_in_base_line(
                base_line, line.company_id
            )
            line.price_subtotal = base_line["tax_details"][
                "raw_total_excluded_currency"
            ]
            line.price_total = base_line["tax_details"]["raw_total_included_currency"]
            line.price_tax = line.price_total - line.price_subtotal

    def _prepare_base_line_for_taxes_computation(self):
        """Convert the current record to a dictionary in order to use the generic taxes
        computation method defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env["account.tax"]._prepare_base_line_for_taxes_computation(
            self,
            tax_ids=self.taxes_id,
            quantity=self.product_qty,
            partner_id=self.order_id.partner_id,
            currency_id=self.order_id.currency_id
            or self.order_id.company_id.currency_id,
            rate=self.order_id.currency_rate,
        )

    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = (
                line.order_id.fiscal_position_id
                or line.order_id.fiscal_position_id._get_fiscal_position(
                    line.order_id.partner_id
                )
            )
            # filter taxes by company
            taxes = line.product_id.supplier_taxes_id._filter_taxes_by_company(
                line.company_id
            )
            line.taxes_id = fpos.map_tax(taxes)

    @api.depends(
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "refund_only",
        "product_uom_qty",
        "order_id.state",
    )
    def _compute_qty_invoiced(self):
        for line in self:
            # compute qty_invoiced
            qty = 0.0
            for inv_line in line.invoice_lines:
                if (
                    inv_line.move_id.state not in ["cancel"]
                    or inv_line.move_id.payment_state == "invoicing_legacy"
                ):
                    if inv_line.move_id.move_type == "in_invoice":
                        qty -= inv_line.product_uom_id._compute_quantity(
                            inv_line.quantity, line.product_uom
                        )
                    elif inv_line.move_id.move_type == "in_refund":
                        qty += inv_line.product_uom_id._compute_quantity(
                            inv_line.quantity, line.product_uom
                        )
            line.qty_invoiced = qty

            # compute qty_to_invoice
            if line.order_id.state in ["purchase", "done"]:
                line.qty_to_invoice = line.product_qty - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.model
    def _prepare_purchase_return_order_line(
        self, product_id, product_qty, product_uom, company_id, supplier, po
    ):
        partner = supplier.partner_id
        uom_po_qty = product_uom._compute_quantity(
            product_qty, product_id.uom_po_id, rounding_method="HALF-UP"
        )
        # _select_seller is used if the supplier have different price depending
        # the quantities ordered.
        today = fields.Date.today()
        seller = product_id.with_company(company_id)._select_seller(
            partner_id=partner,
            quantity=uom_po_qty,
            date=po.date_order and max(po.date_order.date(), today) or today,
            uom_id=product_id.uom_po_id,
        )

        product_taxes = product_id.supplier_taxes_id.filtered(
            lambda x: x.company_id in company_id.parent_ids
        )
        taxes = po.fiscal_position_id.map_tax(product_taxes)

        price_unit = (
            self.env["account.tax"]._fix_tax_included_price_company(
                seller.price, product_taxes, taxes, company_id
            )
            if seller
            else 0
        )

        if (
            price_unit
            and seller
            and po.currency_id
            and seller.currency_id != po.currency_id
        ):
            price_unit = seller.currency_id._convert(
                price_unit,
                po.currency_id,
                po.company_id,
                po.date_order or fields.Date.today(),
            )

        product_lang = product_id.with_prefetch().with_context(
            lang=partner.lang,
            partner_id=partner.id,
        )
        name = product_lang.with_context(seller_id=seller.id).display_name
        if product_lang.description_purchase:
            name += "\n" + product_lang.description_purchase

        date_planned = self.order_id.date_planned or self._get_date_planned(
            seller, po=po
        )

        return {
            "name": name,
            "product_qty": uom_po_qty,
            "product_id": product_id.id,
            "product_uom": product_id.uom_po_id.id,
            "price_unit": price_unit,
            "date_planned": date_planned,
            "taxes_id": [(6, 0, taxes.ids)],
            "order_id": po.id,
        }

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        aml_currency = move and move.currency_id or self.currency_id
        date = move and move.date or fields.Date.today()

        res = {
            "display_type": self.display_type or "product",
            "name": self.env["account.move.line"]._get_journal_items_full_name(
                self.name, self.product_id.display_name
            ),
            "product_id": self.product_id.id,
            "product_uom_id": self.product_uom.id,
            "quantity": (
                -self.qty_to_invoice
                if move and move.move_type == "in_refund"
                else self.qty_to_invoice
            ),
            "price_unit": self.currency_id._convert(
                self.price_unit, aml_currency, self.company_id, date, round=False
            ),
            "tax_ids": [(6, 0, self.taxes_id.ids)],
            "purchase_return_line_id": self.id,
        }
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get(
                "display_type", self.default_get(["display_type"])["display_type"]
            ):
                values.update(
                    product_id=False,
                    price_unit=0,
                    product_uom_qty=0,
                    product_uom=False,
                    date_planned=False,
                )
            else:
                values.update(self._prepare_add_missing_fields(values))

        lines = super().create(vals_list)
        for line in lines:
            if line.product_id and line.order_id.state == "purchase":
                msg = self.env._("Extra line with %s ", line.product_id.display_name)
                line.order_id.message_post(body=msg)
        return lines

    def write(self, values):
        if "display_type" in values and self.filtered(
            lambda line: line.display_type != values.get("display_type")
        ):
            raise UserError(
                self.env._(
                    "You cannot change the type of a purchase return order line. "
                    "Instead you should delete the current line and create "
                    "a new line of the proper type."
                )
            )

        if "product_qty" in values:
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            for line in self:
                if (
                    line.order_id.state == "purchase"
                    and float_compare(
                        line.product_qty,
                        values["product_qty"],
                        precision_digits=precision,
                    )
                    != 0
                ):
                    line.order_id.message_post_with_view(
                        "purchase.track_po_line_template",
                        render_values={
                            "line": line,
                            "product_qty": values["product_qty"],
                        },
                        subtype_xmlid="mail.mt_note",
                    )
        if "qty_delivered" in values:
            for line in self:
                line._track_qty_delivered(values["qty_delivered"])
        return super().write(values)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_purchase_or_done(self):
        for line in self:
            if line.order_id.state in [
                "purchase",
                "done",
            ] and line.display_type not in ["line_note", "line_section"]:
                state_description = {
                    state_desc[0]: state_desc[1]
                    for state_desc in self._fields["state"]._description_selection(
                        self.env
                    )
                }
                raise UserError(
                    self.env._(
                        "Cannot delete a purchase order line which is in state “%s”.",
                        state_description.get(line.state),
                    )
                )

    @api.model
    def _get_date_planned(self, seller, po=False):
        """Return the datetime value to use as Schedule Date (``date_planned``) for
        PO Lines that correspond to the given product.seller_ids,
        when ordered at `date_order_str`.
        :param Model seller: used to fetch the delivery delay (if no seller
                             is provided, the delay is 0)
        :param Model po: purchase.return.order, necessary only if the PO line is
                         not yet attached to a PO.
        :rtype: datetime
        :return: desired Schedule Date for the PO line
        """
        date_order = po.date_order if po else self.order_id.date_order
        if date_order:
            return date_order + relativedelta(days=seller.delay if seller else 0)
        else:
            return datetime.today() + relativedelta(days=seller.delay if seller else 0)

    @api.onchange("product_id")
    def onchange_product_id(self):
        if not self.product_id:
            return

        # Reset date, price and quantity since _onchange_quantity
        # will provide default values
        self.price_unit = self.product_qty = 0.0
        if self.product_id.type in ["consu", "service"]:
            self.refund_only = True
        self._product_id_change()

    def _product_id_change(self):
        if not self.product_id:
            return

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        product_lang = self.product_id.with_context(
            lang=get_lang(self.env, self.partner_id.lang).code,
            partner_id=None,
            company_id=self.company_id.id,
        )
        self.name = self._get_product_purchase_description(product_lang)

        self._compute_tax_id()

    @api.onchange("product_id")
    def onchange_product_id_warning(self):
        if not self.product_id or not self.env.user.has_group(
            "purchase.group_warning_purchase"
        ):
            return
        warning = {}
        title = False
        message = False

        product_info = self.product_id

        if product_info.purchase_line_warn != "no-message":
            title = self.env._("Warning for %s", product_info.name)
            message = product_info.purchase_line_warn_msg
            warning["title"] = title
            warning["message"] = message
            if product_info.purchase_line_warn == "block":
                self.product_id = False
            return {"warning": warning}
        return {}

    @api.depends("product_qty", "product_uom", "company_id", "order_id.partner_id")
    def _compute_price_unit_and_date_planned_and_name(self):
        for line in self:
            if not line.product_id or line.invoice_lines or not line.company_id:
                continue
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

            if seller or not line.date_planned:
                line.date_planned = line._get_date_planned(seller).strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT
                )

            # If not seller, use the standard price.
            # It needs a proper currency conversion.
            if not seller:
                unavailable_seller = line.product_id.seller_ids.filtered(
                    lambda s, line=line: s.partner_id == line.order_id.partner_id
                )
                if (
                    not unavailable_seller
                    and line.price_unit
                    and line.product_uom == line._origin.product_uom
                ):
                    # Avoid to modify the price unit if there is no price list for
                    # this partner and the line has already one to avoid to
                    # override unit price set manually.
                    continue
                po_line_uom = line.product_uom or line.product_id.uom_po_id
                price_unit = line.env["account.tax"]._fix_tax_included_price_company(
                    line.product_id.uom_id._compute_price(
                        line.product_id.standard_price, po_line_uom
                    ),
                    line.product_id.supplier_taxes_id,
                    line.taxes_id,
                    line.company_id,
                )
                price_unit = line.product_id.cost_currency_id._convert(
                    price_unit,
                    line.currency_id,
                    line.company_id,
                    line.date_order or fields.Date.context_today(line),
                    False,
                )
                line.price_unit = float_round(
                    price_unit,
                    precision_digits=max(
                        line.currency_id.decimal_places,
                        self.env["decimal.precision"].precision_get("Product Price"),
                    ),
                )

            elif seller:
                price_unit = (
                    line.env["account.tax"]._fix_tax_included_price_company(
                        seller.price,
                        line.product_id.supplier_taxes_id,
                        line.taxes_id,
                        line.company_id,
                    )
                    if seller
                    else 0.0
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

            # record product names to avoid resetting custom descriptions
            default_names = []
            vendors = line.product_id._prepare_sellers(params=params)
            product_ctx = {
                "seller_id": None,
                "partner_id": None,
                "lang": get_lang(line.env, line.partner_id.lang).code,
            }
            default_names.append(
                line._get_product_purchase_description(
                    line.product_id.with_context(**product_ctx)
                )
            )
            for vendor in vendors:
                product_ctx = {
                    "seller_id": vendor.id,
                    "lang": get_lang(line.env, line.partner_id.lang).code,
                }
                default_names.append(
                    line._get_product_purchase_description(
                        line.product_id.with_context(**product_ctx)
                    )
                )
            if not line.name or line.name in default_names:
                product_ctx = {
                    "seller_id": seller.id,
                    "lang": get_lang(line.env, line.partner_id.lang).code,
                }
                line.name = line._get_product_purchase_description(
                    line.product_id.with_context(**product_ctx)
                )

    @api.depends("product_id", "product_qty", "product_uom")
    def _compute_product_packaging_id(self):
        for line in self:
            # remove packaging if not match the product
            if line.product_packaging_id.product_id != line.product_id:
                line.product_packaging_id = False
            # suggest biggest suitable packaging matching the PO's company
            if line.product_id and line.product_qty and line.product_uom:
                suggested_packaging = line.product_id.packaging_ids.filtered(
                    lambda p, line=line: p.purchase
                    and (p.product_id.company_id <= p.company_id <= line.company_id)
                )._find_suitable_product_packaging(line.product_qty, line.product_uom)
                line.product_packaging_id = (
                    suggested_packaging or line.product_packaging_id
                )

    @api.onchange("product_packaging_id")
    def _onchange_product_packaging_id(self):
        if self.product_packaging_id and self.product_qty:
            newqty = self.product_packaging_id._check_qty(
                self.product_qty, self.product_uom, "UP"
            )
            if (
                float_compare(
                    newqty,
                    self.product_qty,
                    precision_rounding=self.product_uom.rounding,
                )
                != 0
            ):
                return {
                    "warning": {
                        "title": self.env._("Warning"),
                        "message": self.env._(
                            "This product is packaged by "
                            "%(pack_size).2f %(pack_name)s. "
                            "You should purchase %(quantity).2f %(unit)s.",
                            pack_size=self.product_packaging_id.qty,
                            pack_name=self.product_id.uom_id.name,
                            quantity=newqty,
                            unit=self.product_uom.name,
                        ),
                    },
                }

    @api.depends("product_packaging_id", "product_uom", "product_qty")
    def _compute_product_packaging_qty(self):
        self.product_packaging_qty = 0
        for line in self:
            if not line.product_packaging_id:
                continue
            line.product_packaging_qty = line.product_packaging_id._compute_qty(
                line.product_qty, line.product_uom
            )

    @api.depends("product_packaging_qty")
    def _compute_product_qty(self):
        for line in self:
            if line.product_packaging_id:
                packaging_uom = line.product_packaging_id.product_uom_id
                qty_per_packaging = line.product_packaging_id.qty
                product_qty = packaging_uom._compute_quantity(
                    line.product_packaging_qty * qty_per_packaging, line.product_uom
                )
                if (
                    float_compare(
                        product_qty,
                        line.product_qty,
                        precision_rounding=line.product_uom.rounding,
                    )
                    != 0
                ):
                    line.product_qty = product_qty

    @api.depends("product_uom", "product_qty", "product_id.uom_id")
    def _compute_product_uom_qty(self):
        for line in self:
            if line.product_id and line.product_id.uom_id != line.product_uom:
                line.product_uom_qty = line.product_uom._compute_quantity(
                    line.product_qty, line.product_id.uom_id
                )
            else:
                line.product_uom_qty = line.product_qty

    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += "\n" + product_lang.description_purchase

        return name

    @api.model
    def _prepare_add_missing_fields(self, values):
        """Deduce missing required fields from the onchange"""
        res = {}
        onchange_fields = [
            "name",
            "price_unit",
            "product_qty",
            "product_uom",
            "taxes_id",
            "date_planned",
        ]
        if (
            values.get("order_id")
            and values.get("product_id")
            and any(f not in values for f in onchange_fields)
        ):
            line = self.new(values)
            line.onchange_product_id()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    def _get_select_sellers_params(self):
        self.ensure_one()
        return {
            "order_id": self.order_id,
        }
