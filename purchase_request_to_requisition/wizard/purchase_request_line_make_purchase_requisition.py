# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import Command, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _name = "purchase.request.line.make.purchase.requisition"
    _description = "Purchase Request Line Make Purchase Agreement"

    item_ids = fields.One2many(
        comodel_name="purchase.request.line.make.purchase.requisition.item",
        inverse_name="wiz_id",
        string="Items",
    )
    purchase_requisition_id = fields.Many2one(
        comodel_name="purchase.requisition",
        string="Purchase Agreement",
        domain=[("state", "=", "draft")],
    )

    @api.model
    def _prepare_item(self, line):
        return {
            "line_id": line.id,
            "request_id": line.request_id.id,
            "product_id": line.product_id.id,
            "name": line.name or line.product_id.name,
            "product_qty": line.product_qty,
            "product_uom_id": line.product_uom_id.id,
        }

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        # By default, expect called from PR Line
        request_line_obj = self.env["purchase.request.line"]
        request_line_ids = self.env.context.get("active_ids")
        active_model = self.env.context.get("active_model")

        # For case called from PR
        if active_model == "purchase.request":
            request_ids = self.env.context.get("active_ids")
            requests = self.env["purchase.request"].browse(request_ids)
            request_line_ids = requests.mapped("line_ids").ids
            active_model = "purchase.request.line"

        if not request_line_ids:
            return res
        assert active_model == "purchase.request.line", "Bad context propagation"

        request_lines = request_line_obj.browse(request_line_ids)
        items = [Command.create(self._prepare_item(line)) for line in request_lines]
        res["item_ids"] = items
        return res

    @api.model
    def _prepare_purchase_requisition(self, picking_type, group_id, company, origin):
        data = {
            "reference": origin,
            "picking_type_id": picking_type.id,
            "company_id": company.id,
        }
        return data

    @api.model
    def _prepare_purchase_requisition_line(self, pr, item):
        return {
            "requisition_id": pr.id,
            "product_qty": item.product_qty,
            "product_id": item.product_id.id,
            "product_uom_id": item.product_uom_id.id,
            "purchase_request_lines": [(4, item.line_id.id)],
            "analytic_distribution": item.line_id.analytic_distribution,
            "product_description_variants": item.name,
        }

    @api.model
    def _get_requisition_line_search_domain(self, requisition, item):
        vals = [
            ("requisition_id", "=", requisition.id),
            ("product_id", "=", item.product_id.id or False),
            ("product_uom_id", "=", item.product_uom_id.id or False),
        ]
        # Analytic Distribution
        if item.line_id.analytic_distribution:
            analytic_account_ids = list(item.line_id.analytic_distribution.keys())
            vals.append(("analytic_distribution", "in", analytic_account_ids))
        else:
            vals.append(("analytic_distribution", "=", False))
        return vals

    def make_purchase_requisition(self):
        res = []
        purchase_requisition_obj = self.env["purchase.requisition"]
        purchase_requisition_line_obj = self.env["purchase.requisition.line"]
        requisition = False

        for item in self.item_ids:
            line = item.line_id
            if item.product_qty <= 0.0:
                raise UserError(self.env._("Enter a positive quantity."))
            if self.purchase_requisition_id:
                requisition = self.purchase_requisition_id
            if not requisition:
                preq_data = self._prepare_purchase_requisition(
                    line.request_id.picking_type_id,
                    line.request_id.group_id,
                    line.company_id,
                    line.origin,
                )
                requisition = purchase_requisition_obj.create(preq_data)

            # Look for any other Requisition line in the selected Requisition with same
            # product and UoM to sum quantities instead of creating a new
            # requisition line
            domain = self._get_requisition_line_search_domain(requisition, item)
            available_pr_lines = purchase_requisition_line_obj.search(domain)

            # If Unit of Measure is not set, update from wizard.
            if not line.product_uom_id:
                line.product_uom_id = item.product_uom_id

            if available_pr_lines:
                pr_line = available_pr_lines[0]
                pr_line.purchase_request_lines = [(4, line.id)]
                new_qty = pr_line.product_qty + item.product_qty
                pr_line.product_qty = new_qty
            else:
                po_line_data = self._prepare_purchase_requisition_line(
                    requisition, item
                )
                purchase_requisition_line_obj.create(po_line_data)

            res.append(requisition.id)

        purchase_requests = self.item_ids.mapped("request_id")
        purchase_requests.button_in_progress()
        return {
            "domain": [("id", "in", res)],
            "name": self.env._("Purchase Agreement"),
            "view_mode": "list,form",
            "res_model": "purchase.requisition",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }


class PurchaseRequestLineMakePurchaseRequisitionItem(models.TransientModel):
    _name = "purchase.request.line.make.purchase.requisition.item"
    _description = "Purchase Request Line Make Purchase Agreement Item"

    wiz_id = fields.Many2one(
        "purchase.request.line.make.purchase.requisition",
        string="Wizard",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    line_id = fields.Many2one(
        "purchase.request.line",
        string="Purchase Request Line",
        required=True,
    )
    request_id = fields.Many2one(
        "purchase.request",
        related="line_id.request_id",
        string="Purchase Request",
        readonly=True,
    )
    product_id = fields.Many2one("product.product", string="Product")
    name = fields.Char(string="Description", required=True)
    product_qty = fields.Float(
        string="Quantity to Bid",
        digits="Product Unit of Measure",
    )
    product_uom_id = fields.Many2one("uom.uom", string="UoM")

    @api.onchange("product_id", "product_uom_id")
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.display_name
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name
