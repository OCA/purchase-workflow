# Copyright 2013 Joaquín Gutierrez
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3


from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang


class PurchaseCostDistribution(models.Model):
    _name = "purchase.cost.distribution"
    _description = "Purchase landed costs distribution"
    _order = "name desc"

    @api.depends("total_expense", "total_purchase")
    def _compute_amount_total(self):
        for distribution in self:
            distribution.amount_total = (
                distribution.total_purchase + distribution.total_expense
            )

    @api.depends("cost_lines", "cost_lines.total_amount")
    def _compute_total_purchase(self):
        for distribution in self:
            distribution.total_purchase = sum(
                [x.total_amount for x in distribution.cost_lines]
            )

    @api.depends("cost_lines", "cost_lines.product_price_unit")
    def _compute_total_price_unit(self):
        for distribution in self:
            distribution.total_price_unit = sum(
                [x.product_price_unit for x in distribution.cost_lines]
            )

    @api.depends("cost_lines", "cost_lines.product_qty")
    def _compute_total_uom_qty(self):
        for distribution in self:
            distribution.total_uom_qty = sum(
                [x.product_qty for x in distribution.cost_lines]
            )

    @api.depends("cost_lines", "cost_lines.total_weight")
    def _compute_total_weight(self):
        for distribution in self:
            distribution.total_weight = sum(
                [x.total_weight for x in distribution.cost_lines]
            )

    @api.depends("cost_lines", "cost_lines.total_volume")
    def _compute_total_volume(self):
        for distribution in self:
            distribution.total_volume = sum(
                [x.total_volume for x in distribution.cost_lines]
            )

    @api.depends("expense_lines", "expense_lines.expense_amount")
    def _compute_total_expense(self):
        for distribution in self:
            distribution.total_expense = sum(
                [x.expense_amount for x in distribution.expense_lines]
            )

    def _expense_lines_default(self):
        expenses = self.env["purchase.expense.type"].search(
            [("default_expense", "=", True)]
        )
        return [{"type": x, "expense_amount": x.default_amount} for x in expenses]

    name = fields.Char(
        string="Distribution number", required=True, index=True, default="/"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency", string="Currency", related="company_id.currency_id"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("calculated", "Calculated"), ("done", "Done")],
        string="Status",
        readonly=True,
        default="draft",
    )
    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        index=True,
        states={"draft": [("readonly", False)]},
        default=fields.Date.context_today,
    )
    total_uom_qty = fields.Float(
        compute=_compute_total_uom_qty,
        readonly=True,
        digits="Product UoS",
        string="Total quantity",
    )
    total_weight = fields.Float(
        compute=_compute_total_weight,
        string="Total gross weight",
        readonly=True,
        digits="Stock Weight",
    )
    total_volume = fields.Float(
        compute=_compute_total_volume, string="Total volume", readonly=True
    )
    total_purchase = fields.Float(
        compute=_compute_total_purchase, digits="Account", string="Total purchase",
    )
    total_price_unit = fields.Float(
        compute=_compute_total_price_unit,
        string="Total price unit",
        digits="Product Price",
    )
    amount_total = fields.Float(
        compute=_compute_amount_total, digits="Account", string="Total",
    )
    total_expense = fields.Float(
        compute=_compute_total_expense, digits="Account", string="Total expenses",
    )
    note = fields.Text(string="Documentation for this order")
    cost_lines = fields.One2many(
        comodel_name="purchase.cost.distribution.line",
        ondelete="cascade",
        inverse_name="distribution",
        string="Distribution lines",
    )
    expense_lines = fields.One2many(
        comodel_name="purchase.cost.distribution.expense",
        ondelete="cascade",
        inverse_name="distribution",
        string="Expenses",
        default=_expense_lines_default,
    )

    def unlink(self):
        for record in self:
            if record.state not in ("draft", "calculated"):
                raise UserError(_("You can't delete a confirmed cost distribution"))
        return super(PurchaseCostDistribution, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "purchase.cost.distribution"
            )
        return super(PurchaseCostDistribution, self).create(vals)

    def write(self, vals):
        for command in vals.get("cost_lines", []):
            if command[0] in (2, 3, 5):
                if command[0] == 5:
                    to_check = self.mapped("cost_lines").ids
                else:
                    to_check = [command[1]]
                lines = self.mapped("expense_lines.affected_lines").ids
                if any(i in lines for i in to_check):
                    raise UserError(
                        _(
                            "You can't delete a cost line if it's an "
                            "affected line of any expense line."
                        )
                    )
        return super(PurchaseCostDistribution, self).write(vals)

    @api.model
    def _prepare_expense_line(self, expense_line, cost_line):
        distribution = cost_line.distribution
        if expense_line.type.calculation_method == "amount":
            multiplier = cost_line.total_amount
            if expense_line.affected_lines:
                divisor = sum([x.total_amount for x in expense_line.affected_lines])
            else:
                divisor = distribution.total_purchase
        elif expense_line.type.calculation_method == "price":
            multiplier = cost_line.product_price_unit
            if expense_line.affected_lines:
                divisor = sum(
                    [x.product_price_unit for x in expense_line.affected_lines]
                )
            else:
                divisor = distribution.total_price_unit
        elif expense_line.type.calculation_method == "qty":
            multiplier = cost_line.product_qty
            if expense_line.affected_lines:
                divisor = sum([x.product_qty for x in expense_line.affected_lines])
            else:
                divisor = distribution.total_uom_qty
        elif expense_line.type.calculation_method == "weight":
            multiplier = cost_line.total_weight
            if expense_line.affected_lines:
                divisor = sum([x.total_weight for x in expense_line.affected_lines])
            else:
                divisor = distribution.total_weight
        elif expense_line.type.calculation_method == "volume":
            multiplier = cost_line.total_volume
            if expense_line.affected_lines:
                divisor = sum([x.total_volume for x in expense_line.affected_lines])
            else:
                divisor = distribution.total_volume
        elif expense_line.type.calculation_method == "equal":
            multiplier = 1
            divisor = len(expense_line.affected_lines) or len(distribution.cost_lines)
        else:
            raise UserError(_("No valid distribution type."))
        if divisor:
            expense_amount = expense_line.expense_amount * multiplier / divisor
        else:
            raise UserError(
                _(
                    "The cost for the line '%s' can't be "
                    "distributed because the calculation method "
                    "doesn't provide valid data" % expense_line.type.name
                )
            )
        return {
            "distribution_expense": expense_line.id,
            "expense_amount": expense_amount,
            "cost_ratio": expense_amount / cost_line.product_qty,
        }

    def action_calculate(self):
        for distribution in self:
            # Check expense lines for amount 0
            if any([not x.expense_amount for x in distribution.expense_lines]):
                raise UserError(_("Please enter an amount for all the expenses"))
            # Check if exist lines in distribution
            if not distribution.cost_lines:
                raise UserError(_("There is no picking lines in the distribution"))
            # Calculating expense line
            for cost_line in distribution.cost_lines:
                cost_line.expense_lines.unlink()
                expense_lines = []
                for expense in distribution.expense_lines:
                    if (
                        expense.affected_lines
                        and cost_line not in expense.affected_lines
                    ):
                        continue
                    expense_lines.append(self._prepare_expense_line(expense, cost_line))
                cost_line.expense_lines = [(0, 0, x) for x in expense_lines]
            distribution.state = "calculated"
        return True

    def _product_price_update(self, product, vals_list):
        """Method that mimicks stock.move's product_price_update_before_done
        method behaviour, but taking into account that calculations are made
        on an already done moves, and prices sources are given as parameters.
        """
        moves_total_qty = 0
        moves_total_diff_price = 0
        for move, price_diff in vals_list:
            moves_total_qty += move.product_qty
            moves_total_diff_price += move.product_qty * price_diff
        prev_qty_available = product.qty_available - moves_total_qty
        if prev_qty_available <= 0:
            prev_qty_available = 0
        total_available = prev_qty_available + moves_total_qty
        new_std_price = (
            total_available * product.standard_price + moves_total_diff_price
        ) / total_available
        # Write the standard price, as SUPERUSER_ID, because a
        # warehouse manager may not have the right to write on products
        product.sudo().write({"standard_price": new_std_price})

    def action_done(self):
        self.ensure_one()
        self.state = "done"

    def action_draft(self):
        self.ensure_one()
        self.state = "draft"


class PurchaseCostDistributionLine(models.Model):
    _name = "purchase.cost.distribution.line"
    _description = "Purchase cost distribution Line"

    @api.depends("product_price_unit", "product_qty")
    def _compute_total_amount(self):
        for dist_line in self:
            dist_line.total_amount = (
                dist_line.product_price_unit * dist_line.product_qty
            )

    @api.depends("product_id", "product_qty")
    def _compute_total_weight(self):
        for dist_line in self:
            dist_line.total_weight = dist_line.product_weight * dist_line.product_qty

    @api.depends("product_id", "product_qty")
    def _compute_total_volume(self):
        for dist_line in self:
            dist_line.total_volume = dist_line.product_volume * dist_line.product_qty

    @api.depends("expense_lines", "expense_lines.cost_ratio")
    def _compute_cost_ratio(self):
        for dist_line in self:
            dist_line.cost_ratio = sum([x.cost_ratio for x in dist_line.expense_lines])

    @api.depends("expense_lines", "expense_lines.expense_amount")
    def _compute_expense_amount(self):
        for dist_line in self:
            dist_line.expense_amount = sum(
                [x.expense_amount for x in dist_line.expense_lines]
            )

    @api.depends("standard_price_old", "cost_ratio")
    def _compute_standard_price_new(self):
        for dist_line in self:
            dist_line.standard_price_new = (
                dist_line.standard_price_old + dist_line.cost_ratio
            )

    @api.depends(
        "distribution",
        "distribution.name",
        "picking_id",
        "picking_id.name",
        "product_id",
        "product_id.display_name",
    )
    def _compute_name(self):
        for dist_line in self:
            dist_line.name = "{}: {} / {}".format(
                dist_line.distribution.name,
                dist_line.picking_id.name,
                dist_line.product_id.display_name,
            )

    @api.depends("move_id", "move_id.product_id")
    def _compute_product_id(self):
        for dist_line in self:
            # Cannot be done via related
            # field due to strange bug in update chain
            dist_line.product_id = dist_line.move_id.product_id.id

    @api.depends("move_id", "move_id.product_qty")
    def _compute_product_qty(self):
        for dist_line in self:
            # Cannot be done via related
            #  field due to strange bug in update chain
            dist_line.product_qty = dist_line.move_id.product_qty

    @api.depends("move_id")
    def _compute_standard_price_old(self):
        for dist_line in self:
            dist_line.standard_price_old = (
                dist_line.move_id and dist_line.move_id._get_price_unit() or 0.0
            )

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    distribution = fields.Many2one(
        comodel_name="purchase.cost.distribution",
        string="Cost distribution",
        ondelete="cascade",
        required=True,
    )
    move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Picking line",
        ondelete="restrict",
        required=True,
    )
    purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Purchase order line",
        related="move_id.purchase_line_id",
    )
    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase order",
        readonly=True,
        related="move_id.purchase_line_id.order_id",
        store=True,
    )
    partner = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        readonly=True,
        related="move_id.purchase_line_id.order_id.partner_id",
    )
    picking_id = fields.Many2one(
        "stock.picking", string="Picking", related="move_id.picking_id", store=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        store=True,
        compute="_compute_product_id",
    )
    product_qty = fields.Float(
        string="Quantity", compute="_compute_product_qty", store=True
    )
    product_uom = fields.Many2one(
        comodel_name="uom.uom", string="Unit of measure", related="move_id.product_uom"
    )
    product_price_unit = fields.Float(string="Unit price", related="move_id.price_unit")
    expense_lines = fields.One2many(
        comodel_name="purchase.cost.distribution.line.expense",
        inverse_name="distribution_line",
        string="Expenses distribution lines",
    )
    product_volume = fields.Float(
        string="Volume",
        help="The volume in m3.",
        related="product_id.product_tmpl_id.volume",
    )
    product_weight = fields.Float(
        string="Gross weight",
        related="product_id.product_tmpl_id.weight",
        help="The gross weight in Kg.",
    )
    standard_price_old = fields.Float(
        string="Previous cost",
        compute="_compute_standard_price_old",
        store=True,
        digits="Product Price",
    )
    expense_amount = fields.Float(
        string="Cost amount", digits="Account", compute="_compute_expense_amount",
    )
    cost_ratio = fields.Float(string="Unit cost", compute="_compute_cost_ratio")
    standard_price_new = fields.Float(
        string="New cost",
        digits="Product Price",
        compute="_compute_standard_price_new",
    )
    total_amount = fields.Float(
        compute=_compute_total_amount, string="Amount line", digits="Account",
    )
    total_weight = fields.Float(
        compute=_compute_total_weight,
        string="Line weight",
        store=True,
        digits="Stock Weight",
        help="The line gross weight in Kg.",
    )
    total_volume = fields.Float(
        compute=_compute_total_volume,
        string="Line volume",
        store=True,
        help="The line volume in m3.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company", related="distribution.company_id", store=True,
    )

    @api.model
    def get_action_purchase_cost_distribution(self):
        xml_id = "purchase_landed_cost.action_purchase_cost_distribution"
        action = self.env.ref(xml_id).read()[0]
        distributions = self.mapped("distribution")
        if len(distributions) == 1:
            form = self.env.ref("purchase_landed_cost.purchase_cost_distribution_form")
            action["views"] = [(form.id, "form")]
            action["res_id"] = distributions.id
        else:
            action["domain"] = [("id", "in", distributions.ids)]
        return action


class PurchaseCostDistributionLineExpense(models.Model):
    _name = "purchase.cost.distribution.line.expense"
    _description = "Purchase cost distribution line expense"

    distribution_line = fields.Many2one(
        comodel_name="purchase.cost.distribution.line",
        string="Cost distribution line",
        ondelete="cascade",
    )
    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        store=True,
        readonly=True,
        related="distribution_line.picking_id",
    )
    picking_date_done = fields.Datetime(
        related="picking_id.date_done", store=True, readonly=True,
    )
    distribution_expense = fields.Many2one(
        comodel_name="purchase.cost.distribution.expense",
        string="Distribution expense",
        ondelete="cascade",
    )
    type = fields.Many2one(
        "purchase.expense.type",
        string="Expense type",
        readonly=True,
        related="distribution_expense.type",
        store=True,
    )
    expense_amount = fields.Float(string="Expense amount", digits="Account",)
    cost_ratio = fields.Float("Unit cost")
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="distribution_line.company_id",
        store=True,
        readonly=True,
    )


class PurchaseCostDistributionExpense(models.Model):
    _name = "purchase.cost.distribution.expense"
    _description = "Purchase cost distribution expense"

    @api.depends("distribution", "distribution.cost_lines")
    def _compute_imported_lines(self):
        for record in self:
            record.imported_lines = record.env["purchase.cost.distribution.line"]
            record.imported_lines |= record.distribution.cost_lines

    distribution = fields.Many2one(
        comodel_name="purchase.cost.distribution",
        string="Cost distribution",
        index=True,
        ondelete="cascade",
        required=True,
    )
    ref = fields.Char(string="Reference")
    type = fields.Many2one(
        comodel_name="purchase.expense.type",
        string="Expense type",
        index=True,
        ondelete="restrict",
    )
    calculation_method = fields.Selection(
        string="Calculation method", related="type.calculation_method", readonly=True
    )
    imported_lines = fields.Many2many(
        comodel_name="purchase.cost.distribution.line",
        string="Imported lines",
        compute="_compute_imported_lines",
    )
    affected_lines = fields.Many2many(
        comodel_name="purchase.cost.distribution.line",
        column1="expense_id",
        relation="distribution_expense_aff_rel",
        column2="line_id",
        string="Affected lines",
        help="Put here specific lines that this expense is going to be "
        "distributed across. Leave it blank to use all imported lines.",
        domain="[('id', 'in', imported_lines)]",
    )
    expense_amount = fields.Float(
        string="Expense amount", digits="Account", required=True
    )
    invoice_line = fields.Many2one(
        comodel_name="account.move.line",
        string="Supplier invoice line",
        domain="[('invoice_id.type', '=', 'in_invoice'),"
        "('invoice_id.state', '=', 'posted')]",
    )
    invoice_id = fields.Many2one(comodel_name="account.move", string="Invoice")
    display_name = fields.Char(compute="_compute_display_name", store=True)
    company_id = fields.Many2one(
        comodel_name="res.company", related="distribution.company_id", store=True,
    )

    @api.depends("distribution", "type", "expense_amount", "ref")
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{}: {} - {} ({})".format(
                record.distribution.name,
                record.type.name,
                record.ref,
                formatLang(
                    record.env,
                    record.expense_amount,
                    currency_obj=record.distribution.currency_id,
                ),
            )

    @api.onchange("type")
    def onchange_type(self):
        """set expense_amount in the currency of the distribution"""
        if self.type and self.type.default_amount:
            currency_from = self.type.company_id.currency_id
            amount = self.type.default_amount
            currency_to = self.distribution.currency_id
            company = self.company_id or self.env.user.company_id
            cost_date = self.distribution.date or fields.Date.today()
            self.expense_amount = currency_from._convert(
                amount, currency_to, company, cost_date
            )

    @api.onchange("invoice_line")
    def onchange_invoice_line(self):
        """set expense_amount in the currency of the distribution"""
        self.invoice_id = self.invoice_line.invoice_id.id
        currency_from = self.invoice_line.company_id.currency_id
        amount = self.invoice_line.price_subtotal
        currency_to = self.distribution.currency_id
        company = self.company_id or self.env.user.company_id
        cost_date = self.distribution.date or fields.Date.today()
        self.expense_amount = currency_from._convert(
            amount, currency_to, company, cost_date
        )

    def button_duplicate(self):
        for expense in self:
            expense.copy()
