# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, fields, models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    purchase_request_count = fields.Integer(
        compute="_compute_purchase_request_count",
    )

    @api.model
    def _purchase_request_confirm_message_content(self, pr, request, request_dict):
        if not request_dict:
            request_dict = {}
        title = _("Bid confirmation %s for your Request %s") % (pr.name, request.name)
        message = "<h3>%s</h3><ul>" % title
        message += _(
            "The following requested items from Purchase Request %s "
            "have now being sent to Suppliers using Purchase Bid "
            "%s:"
        ) % (request.name, pr.name)

        for line in request_dict.values():
            message += _("<li><b>%s</b>: Total bid quantity %s %s</li>") % (
                line["name"],
                line["product_qty"],
                line["product_uom_id"],
            )
        message += "</ul>"
        return message

    def _purchase_request_confirm_message(self):
        request_obj = self.env["purchase.request"]
        for pr in self:
            requests_dict = {}
            for line in pr.line_ids:
                for request_line in line.purchase_request_lines:
                    request_id = request_line.request_id.id
                    if request_id not in requests_dict:
                        requests_dict[request_id] = {}
                    data = {
                        "name": request_line.name,
                        "product_qty": line.product_qty,
                        "product_uom_id": line.product_uom_id.name,
                    }
                    requests_dict[request_id][request_line.id] = data
            for request_id in requests_dict.keys():
                request = request_obj.browse(request_id)
                message = self._purchase_request_confirm_message_content(
                    pr, request, requests_dict[request_id]
                )
                request.message_post(body=message, subtype_xmlid="mail.mt_comment")
        return True

    def action_in_progress(self):
        res = super().action_in_progress()
        self._purchase_request_confirm_message()
        return res

    def _compute_purchase_request_count(self):
        for rec in self:
            rec.purchase_request_count = len(
                rec.mapped("line_ids.purchase_request_lines.request_id")
            )

    def action_view_purchase_request(self):
        action = (
            self.env.ref("purchase_request.purchase_request_form_action")
            .sudo()
            .read()[0]
        )
        requests = self.mapped("line_ids.purchase_request_lines.request_id")
        if len(requests) > 1:
            action["domain"] = [("id", "in", requests.ids)]
        elif requests:
            action["views"] = [
                (self.env.ref("purchase_request.view_purchase_request_form").id, "form")
            ]
            action["res_id"] = requests.id
        action["context"] = {}
        return action


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    def _compute_has_purchase_request_lines(self):
        for rec in self:
            rec.has_purchase_request_lines = bool(rec.purchase_request_lines)

    purchase_request_lines = fields.Many2many(
        "purchase.request.line",
        "purchase_request_purchase_requisition_line_rel",
        "purchase_requisition_line_id",
        "purchase_request_line_id",
        string="Purchase Request Lines",
        readonly=True,
        copy=False,
    )
    has_purchase_request_lines = fields.Boolean(
        compute="_compute_has_purchase_request_lines",
        string="Has Purchase Request Lines",
    )

    def action_openRequestLineTreeView(self):
        """
        :return dict: dictionary value for created view
        """
        request_line_ids = []
        for line in self:
            request_line_ids = [
                request_line.id for request_line in line.purchase_request_lines
            ]
        domain = [("id", "in", request_line_ids)]

        return {
            "name": _("Purchase Request Lines"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.request.line",
            "view_type": "form",
            "view_mode": "tree,form",
            "domain": domain,
        }

    def _prepare_purchase_order_line(
        self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False
    ):
        res = super()._prepare_purchase_order_line(
            name, product_qty, price_unit, taxes_ids
        )
        pr_lines = self.mapped("purchase_request_lines")
        res["purchase_request_lines"] = (
            pr_lines and [(4, line.id) for line in pr_lines] or []
        )
        return res
