# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseAutoValidation(models.Model):
    _name = "purchase.auto.validation"
    _description = "Purchase Auto Validation"

    name = fields.Char(compute="_compute_name", store=True)

    product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        string="Products",
    )

    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Product Variants",
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        required=True,
    )
    weekday = fields.Selection(
        selection="_selection_weekday",
        string="Day",
        required=True,
    )
    hour = fields.Integer(
        string="Hour",
        required=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
    )
    purchase_order_ids = fields.One2many(
        comodel_name="purchase.order",
        inverse_name="purchase_auto_validation_id",
        string="Purchase Orders",
        readonly=True,
    )

    def _get_covered_product_ids(self):
        self.ensure_one()
        return set(self.product_ids.ids) | set(
            self.product_tmpl_ids.mapped("product_variant_ids").ids
        )

    @api.constrains("product_ids", "product_tmpl_ids", "company_id", "active")
    def _check_products_uniq_per_company(self):
        active_rules = self.search([("active", "=", True)])
        for rule in self.filtered("active"):
            covered_ids = rule._get_covered_product_ids()
            if not covered_ids:
                continue
            for other in active_rules - rule:
                if (
                    rule.company_id
                    and other.company_id
                    and rule.company_id != other.company_id
                ):
                    continue
                overlap = covered_ids & other._get_covered_product_ids()
                if overlap:
                    products = self.env["product.product"].browse(overlap)
                    raise ValidationError(
                        _(
                            "The following products are already covered by "
                            "another auto purchase validation rule for the "
                            "same company (or a rule without company): %s"
                        )
                        % ", ".join(products.mapped("display_name"))
                    )

    def _selection_weekday(self):
        return [
            ("0", _("Monday")),
            ("1", _("Tuesday")),
            ("2", _("Wednesday")),
            ("3", _("Thursday")),
            ("4", _("Friday")),
            ("5", _("Saturday")),
            ("6", _("Sunday")),
        ]

    @api.depends("weekday", "hour")
    def _compute_name(self):
        weekday_dict = dict(self._selection_weekday())
        for record in self:
            record.name = (
                f"{dict(weekday_dict).get(record.weekday, '')}: {record.hour}: 00"
            )

    @api.model
    def _get_purchase_to_validate(self, weekday, hour):
        rules = self.search([("weekday", "=", weekday)])
        return rules.filtered(lambda config: config.hour <= hour)

    def _validate_purchase_orders(self):
        orders = self.env["purchase.order"].search(
            [
                ("purchase_auto_validation_id", "in", self.ids),
                ("state", "=", "draft"),
            ]
        )
        orders.button_confirm()

    @api.model
    def _cron_validate_auto_purchase_orders(self):
        now = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        weekday = str(now.weekday())
        rules = self._get_purchase_to_validate(weekday, now.hour)
        rules._validate_purchase_orders()
