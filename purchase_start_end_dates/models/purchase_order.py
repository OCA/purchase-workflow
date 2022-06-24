# Copyright 2022 elego Software Solutions, Germany (https://www.elegosoft.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    default_start_date = fields.Date(string="Default Start Date")
    default_end_date = fields.Date(string="Default End Date")

    @api.constrains("default_start_date", "default_end_date")
    def _check_default_start_end_dates(self):
        if (
            self.default_start_date
            and self.default_end_date
            and self.default_start_date > self.default_end_date
        ):
            raise ValidationError(
                _(
                    "Default Start Date should be before or be the "
                    "same as Default End Date for purchase order '%s'."
                )
                % self.display_name
            )

    @api.onchange("default_start_date")
    def default_start_date_change(self):
        if (
            self.default_start_date
            and self.default_end_date
            and self.default_start_date > self.default_end_date
        ):
            self.default_end_date = self.default_start_date

    @api.onchange("default_end_date")
    def default_end_date_change(self):
        if (
            self.default_start_date
            and self.default_end_date
            and self.default_start_date > self.default_end_date
        ):
            self.default_start_date = self.default_end_date


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    start_date = fields.Date(
        string="Start Date", readonly=True, states={"draft": [("readonly", False)]}
    )
    end_date = fields.Date(
        string="End Date", readonly=True, states={"draft": [("readonly", False)]}
    )
    number_of_days = fields.Integer(
        compute="_compute_number_of_days",
        inverse="_inverse_number_of_days",
        string="Number of Days",
        readonly=False,
        store=True,
    )
    must_have_dates = fields.Boolean(related="product_id.must_have_dates")

    @api.depends("start_date", "end_date")
    def _compute_number_of_days(self):
        for line in self:
            days = False
            if line.start_date and line.end_date:
                days = (line.end_date - line.start_date).days + 1
            line.number_of_days = days

    @api.onchange("number_of_days")
    def _inverse_number_of_days(self):
        res = {"warning": {}}
        for line in self:
            if line.number_of_days < 0:
                res["warning"]["title"] = _("Wrong number of days")
                res["warning"]["message"] = _(
                    "On purchase order line with product '%s', the "
                    "number of days is negative (%d) ; this is not "
                    "allowed. The number of days has been forced to 1."
                ) % (line.product_id.display_name, line.number_of_days)
                line.number_of_days = 1
            if line.start_date:
                line.end_date = line.start_date + relativedelta(
                    days=line.number_of_days - 1
                )
            elif line.end_date:
                line.start_date = line.end_date - relativedelta(
                    days=line.number_of_days - 1
                )
        return res

    @api.constrains("start_date", "end_date")
    def _check_start_end_dates(self):
        for line in self:
            if line.must_have_dates:
                if not line.start_date:
                    raise ValidationError(
                        _(
                            "Missing Start Date for purchase order line with "
                            "Product '%s'."
                        )
                        % (line.product_id.name)
                    )
                if not line.end_date:
                    raise ValidationError(
                        _(
                            "Missing End Date for purchase order line with "
                            "Product '%s'."
                        )
                        % (line.product_id.name)
                    )
                if line.start_date > line.end_date:
                    raise ValidationError(
                        _(
                            "Start Date should be before or be the same as "
                            "End Date for purchase order line with Product '%s'."
                        )
                        % (line.product_id.name)
                    )

    @api.onchange("end_date")
    def end_date_change(self):
        if self.end_date:
            if self.start_date and self.start_date > self.end_date:
                self.start_date = self.end_date

    @api.onchange("start_date")
    def start_date_change(self):
        if self.start_date:
            if self.end_date and self.start_date > self.end_date:
                self.end_date = self.start_date

    @api.onchange("product_id")
    def start_end_dates_product_id_change(self):
        if self.product_id.must_have_dates:
            if self.order_id.default_start_date:
                self.start_date = self.order_id.default_start_date
            else:
                self.start_date = False
            if self.order_id.default_end_date:
                self.end_date = self.order_id.default_end_date
            else:
                self.end_date = False
        else:
            self.start_date = False
            self.end_date = False
