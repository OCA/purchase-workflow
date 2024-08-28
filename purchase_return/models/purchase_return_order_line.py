# Copyright 2004-2021 Odoo S.A.
# Copyright 2021 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import datetime, time

from dateutil.relativedelta import relativedelta
from pytz import UTC, timezone

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import get_lang


class PurchaseReturnOrderLine(models.Model):
    _name = "purchase.return.order.line"
    _description = "Purchase Return Order Line"
    _order = "order_id, sequence, id"

    name = fields.Text(string="Description", required=True)
    sequence = fields.Integer(string="Sequence Line", default=10)
    product_qty = fields.Float(
        string="Quantity", digits="Product Unit of Measure", required=True
    )
    product_uom_qty = fields.Float(
        string="Total Quantity", compute="_compute_product_uom_qty", store=True
    )
    date_planned = fields.Datetime(
        string="Delivery Date",
        help="Delivery date expected from vendor. "
        "This date respectively defaults to vendor pricelist "
        "lead time then today's date.",
    )
    taxes_id = fields.Many2many(
        "account.tax",
        string="Taxes",
        domain=["|", ("active", "=", False), ("active", "=", True)],
    )
    product_uom = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain=[("purchase_ok", "=", True)],
        change_default=True,
    )
    product_type = fields.Selection(related="product_id.type", readonly=True)
    price_unit = fields.Float(
        string="Unit Price", required=True, digits="Product Price"
    )

    price_subtotal = fields.Monetary(
        compute="_compute_amount", string="Subtotal", store=True
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
    account_analytic_id = fields.Many2one(
        "account.analytic.account",
        store=True,
        string="Analytic Account",
        readonly=False,
    )
    company_id = fields.Many2one(
        "res.company",
        related="order_id.company_id",
        string="Company",
        store=True,
        readonly=True,
    )
    state = fields.Selection(related="order_id.state", store=True, readonly=False)
    invoice_lines = fields.One2many(
        "account.move.line",
        "purchase_return_line_id",
        string="Bill Lines",
        readonly=True,
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
        readonly=True,
        digits="Product Unit of Measure",
    )

    partner_id = fields.Many2one(
        "res.partner",
        related="order_id.partner_id",
        string="Partner",
        readonly=True,
        store=True,
    )
    currency_id = fields.Many2one(
        related="order_id.currency_id", store=True, string="Currency", readonly=True
    )
    date_order = fields.Datetime(
        related="order_id.date_order", string="Order Date", readonly=True
    )

    display_type = fields.Selection(
        [("product", "Product"), ("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )

    _sql_constraints = [
        (
            "accountable_required_fields",
            "CHECK(display_type IS NOT 'product' OR (product_id IS NOT NULL "
            "AND product_uom IS NOT NULL AND date_planned IS NOT NULL))",
            "Missing required fields on accountable purchase return order line.",
        ),
        (
            "non_accountable_null_fields",
            "CHECK(display_type IS 'product' OR (product_id IS NULL "
            "AND price_unit = 0 AND product_uom_qty = 0 AND product_uom "
            "IS NULL AND date_planned is NULL))",
            "Forbidden values on non-accountable purchase return order line",
        ),
    ]

    @api.depends("product_qty", "price_unit", "taxes_id")
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals["price_unit"],
                vals["currency_id"],
                vals["product_qty"],
                vals["product"],
                vals["partner"],
            )
            line.update(
                {
                    "price_tax": sum(
                        t.get("amount", 0.0) for t in taxes.get("taxes", [])
                    ),
                    "price_total": taxes["total_included"],
                    "price_subtotal": taxes["total_excluded"],
                }
            )

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            "price_unit": self.price_unit,
            "currency_id": self.order_id.currency_id,
            "product_qty": self.product_qty,
            "product": self.product_id,
            "partner": self.order_id.partner_id,
        }

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
            taxes = line.product_id.supplier_taxes_id.filtered(
                lambda r: r.company_id == line.env.company
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
                if inv_line.move_id.state not in ["cancel"]:
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
        partner = supplier.name
        uom_po_qty = product_uom._compute_quantity(product_qty, product_id.uom_po_id)
        # _select_seller is used if the supplier have different price depending
        # the quantities ordered.
        seller = product_id.with_company(company_id)._select_seller(
            partner_id=partner,
            quantity=uom_po_qty,
            date=po.date_order and po.date_order.date(),
            uom_id=product_id.uom_po_id,
        )

        taxes = product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(taxes, product_id, seller.name)
        if taxes_id:
            taxes_id = taxes_id.filtered(lambda x: x.company_id.id == company_id.id)

        price_unit = (
            self.env["account.tax"]._fix_tax_included_price_company(
                seller.price, product_id.supplier_taxes_id, taxes_id, company_id
            )
            if seller
            else 0.0
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
        name = product_lang.display_name
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
            "taxes_id": [(6, 0, taxes_id.ids)],
            "order_id": po.id,
        }

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = {
            "display_type": "product",
            "sequence": self.sequence,
            "name": "%s: %s" % (self.order_id.name, self.name),
            "product_id": self.product_id.id,
            "product_uom_id": self.product_uom.id,
            "quantity": self.qty_to_invoice,
            "price_unit": self.price_unit,
            "tax_ids": [(6, 0, self.taxes_id.ids)],
            "purchase_return_line_id": self.id,
        }
        if not move:
            return res

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        res.update(
            {
                "move_id": move.id,
                "currency_id": currency and currency.id or False,
                "date_maturity": move.invoice_date_due,
                "partner_id": move.partner_id.id,
            }
        )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get("display_type") != "product":
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
                msg = _("Extra line with %s ") % (line.product_id.display_name,)
                line.order_id.message_post(body=msg)
        return lines

    def write(self, values):
        if "display_type" in values and self.filtered(
            lambda line: line.display_type != values.get("display_type")
        ):
            raise UserError(
                _(
                    "You cannot change the type of a purchase return order line. "
                    "Instead you should delete the current line and create "
                    "a new line of the proper type."
                )
            )

        if "product_qty" in values:
            for line in self:
                if line.order_id.state == "purchase":
                    line.order_id.message_post_with_view(
                        "purchase.track_po_line_template",
                        values={"line": line, "product_qty": values["product_qty"]},
                        subtype_id=self.env.ref("mail.mt_note").id,
                    )
        if "qty_delivered" in values:
            for line in self:
                line._track_qty_delivered(values["qty_delivered"])
        return super(PurchaseReturnOrderLine, self).write(values)

    def unlink(self):
        for line in self:
            if line.order_id.state in ["purchase", "done"]:
                raise UserError(
                    _("Cannot delete a purchase order line which is in state '%s'.")
                    % (line.state,)
                )
        return super(PurchaseReturnOrderLine, self).unlink()

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
            date_planned = date_order + relativedelta(
                days=seller.delay if seller else 0
            )
        else:
            date_planned = datetime.today() + relativedelta(
                days=seller.delay if seller else 0
            )
        return self._convert_to_middle_of_day(date_planned)

    @api.onchange("product_id")
    def onchange_product_id(self):
        if not self.product_id:
            return

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.price_unit = self.product_qty = 0.0
        if self.product_id.type in ["consu", "service"]:
            self.refund_only = True
        self._product_id_change()
        self._onchange_quantity()

    def _product_id_change(self):
        if not self.product_id:
            return

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        product_lang = self.product_id.with_context(
            lang=get_lang(self.env, self.partner_id.lang).code,
            partner_id=self.partner_id.id,
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
            title = _("Warning for %s", product_info.name)
            message = product_info.purchase_line_warn_msg
            warning["title"] = title
            warning["message"] = message
            if product_info.purchase_line_warn == "block":
                self.product_id = False
            return {"warning": warning}
        return {}

    @api.onchange("product_qty", "product_uom")
    def _onchange_quantity(self):
        if not self.product_id:
            return
        params = {"order_id": self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params,
        )

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(
                DEFAULT_SERVER_DATETIME_FORMAT
            )

        # If not seller, use the standard price. It needs a proper currency conversion.
        if not seller:
            price_unit = self.env["account.tax"]._fix_tax_included_price_company(
                self.product_id.uom_id._compute_price(
                    self.product_id.standard_price, self.product_id.uom_po_id
                ),
                self.product_id.supplier_taxes_id,
                self.taxes_id,
                self.company_id,
            )
            if (
                price_unit
                and self.order_id.currency_id
                and self.order_id.company_id.currency_id != self.order_id.currency_id
            ):
                price_unit = self.order_id.company_id.currency_id._convert(
                    price_unit,
                    self.order_id.currency_id,
                    self.order_id.company_id,
                    self.date_order or fields.Date.today(),
                )

            if self.product_uom:
                price_unit = self.product_id.uom_id._compute_price(
                    price_unit, self.product_uom
                )

            self.price_unit = price_unit
            return

        price_unit = (
            self.env["account.tax"]._fix_tax_included_price_company(
                seller.price,
                self.product_id.supplier_taxes_id,
                self.taxes_id,
                self.company_id,
            )
            if seller
            else 0.0
        )
        if (
            price_unit
            and seller
            and self.order_id.currency_id
            and seller.currency_id != self.order_id.currency_id
        ):
            price_unit = seller.currency_id._convert(
                price_unit,
                self.order_id.currency_id,
                self.order_id.company_id,
                self.date_order or fields.Date.today(),
            )

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        self.price_unit = price_unit

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

    def _convert_to_middle_of_day(self, date):
        """Return a datetime which is the noon of the input date(time) according
        to order user's time zone, convert to UTC time.
        """
        return (
            timezone(self.order_id.user_id.tz or self.company_id.partner_id.tz or "UTC")
            .localize(datetime.combine(date, time(12)))
            .astimezone(UTC)
            .replace(tzinfo=None)
        )
