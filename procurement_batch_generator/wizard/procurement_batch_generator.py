# Copyright 2014-2021 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero
from odoo.tools.misc import clean_context


class ProcurementBatchGenerator(models.TransientModel):
    _name = "procurement.batch.generator"
    _description = "Wizard to create procurements from product tree"

    company_id = fields.Many2one("res.company", string="Company", required=True)
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        required=True,
        domain="[('company_id', '=', company_id)]",
    )
    line_ids = fields.One2many(
        "procurement.batch.generator.line",
        "parent_id",
        string="Procurement Request Lines",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "company_id" in fields_list and "company_id" not in res:
            res["company_id"] = self.env.company.id
        if "warehouse_id" in fields_list and "warehouse_id" not in res:
            wh = self.env["stock.warehouse"].search(
                [("company_id", "=", res["company_id"])], limit=1
            )
            res["warehouse_id"] = wh and wh.id or False
        assert isinstance(
            self.env.context["active_ids"], list
        ), "context['active_ids'] must be a list"
        src_models = ("product.product", "product.template")
        assert self.env.context["active_model"] in src_models
        today = fields.Date.context_today(self)
        res["line_ids"] = []
        if "line_ids" in fields_list:
            for active_id in self.env.context["active_ids"]:
                if self.env.context["active_model"] == "product.product":
                    product = self.env["product.product"].browse(active_id)
                    product_tmpl = product.product_tmpl_id
                elif self.env.context["active_model"] == "product.template":
                    product_tmpl = self.env["product.template"].browse(active_id)
                    product = product_tmpl.product_variant_id
                has_variants = False
                if len(product_tmpl.product_variant_ids) > 1:
                    has_variants = True
                partner_id = (
                    product.seller_ids and product.seller_ids[0].name.id or False
                )
                res["line_ids"].append(
                    (
                        0,
                        0,
                        {
                            "product_has_variants": has_variants,
                            "product_tmpl_id": product_tmpl.id,
                            "product_id": product.id,
                            "partner_id": partner_id,
                            "qty_available": product.qty_available,
                            "outgoing_qty": product.outgoing_qty,
                            "incoming_qty": product.incoming_qty,
                            "uom_id": product.uom_id.id,
                            "procurement_qty": 0.0,
                            "date_planned": today,
                        },
                    )
                )
        return res

    def validate(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("There are no lines!"))
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        pgo = self.env["procurement.group"]
        proc_list = []
        group = pgo.create(self._prepare_procurement_group())
        for line in self.line_ids:
            if float_is_zero(line.procurement_qty, precision_digits=prec):
                continue
            if float_compare(line.procurement_qty, 0, precision_digits=prec) < 0:
                raise UserError(
                    _("The requested quantity cannot be negative for product '%s'.")
                    % line.product_id.display_name
                )
            proc_list.append(
                pgo.Procurement(
                    line.product_id,
                    line.procurement_qty,
                    line.product_id.uom_id,
                    self.warehouse_id.lot_stock_id,
                    _("Manual Replenishment"),  # name
                    _("Manual Replenishment"),  # origin
                    self.company_id,
                    line._prepare_run_values(group),
                )
            )  # values

        pgo.with_context(clean_context(self.env.context)).run(proc_list)

    def _prepare_procurement_group(self):
        self.ensure_one()
        vals = {"partner_id": self.env.user.partner_id.id}
        return vals


class ProcurementBatchGeneratorLine(models.TransientModel):
    _name = "procurement.batch.generator.line"
    _description = "Lines of the wizard to request procurements"

    parent_id = fields.Many2one(
        "procurement.batch.generator", string="Parent", ondelete="cascade"
    )
    company_id = fields.Many2one(related="parent_id.company_id")
    product_tmpl_id = fields.Many2one(
        "product.template", string="Product Template", required=True
    )
    product_has_variants = fields.Boolean(string="Has variants")
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        domain="[('product_tmpl_id', '=', product_tmpl_id)]",
    )
    partner_id = fields.Many2one("res.partner", string="Supplier")
    qty_available = fields.Float(
        string="Qty Available", digits="Product Unit of Measure"
    )
    outgoing_qty = fields.Float(digits="Product Unit of Measure")
    incoming_qty = fields.Float(digits="Product Unit of Measure")
    procurement_qty = fields.Float(
        string="Requested Qty", digits="Product Unit of Measure", required=True
    )
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure", readonly=True)
    date_planned = fields.Date(string="Scheduled Date", required=True)
    route_ids = fields.Many2many(
        "stock.location.route",
        string="Preferred Routes",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    def _prepare_run_values(self, group):
        self.ensure_one()
        vals = {
            "warehouse_id": self.parent_id.warehouse_id,
            "route_ids": self.route_ids,
            "date_planned": self.date_planned,
            "group_id": group,
        }
        return vals
