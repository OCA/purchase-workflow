# Copyright 2022 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    # override to change returned domain based on company settings
    @api.model
    def _make_pr_get_domain(self, values):
        domain = super()._make_pr_get_domain(values)
        lst_domain = [dom for dom in domain]
        lst_domain.pop(0)
        lst_domain += [
            ("state", "in", ("draft", "to_approve", "approved")),
        ]
        domain = tuple(lst_domain)
        return domain

    # override method from purchase_request to change existing pr handling
    def create_purchase_request(self, procurement_group):
        procurement = procurement_group[0]
        rule = procurement_group[1]
        purchase_request_model = self.env["purchase.request"]
        purchase_request_line_model = self.env["purchase.request.line"]
        cache = {}
        pr = self.env["purchase.request"]
        domain = rule._make_pr_get_domain(procurement.values)
        if domain in cache:
            pr = cache[domain]
        elif domain:
            pr = (
                self.env["purchase.request"]
                .search([dom for dom in domain])
                .filtered(
                    lambda x: procurement.product_id in x.line_ids.mapped("product_id")
                    and x.purchase_count == 0
                )
            )
            pr = pr[0] if pr else False
            cache[domain] = pr
        if not pr:
            request_data = rule._prepare_purchase_request(
                procurement.origin, procurement.values
            )
            pr = purchase_request_model.create(request_data)
            cache[domain] = pr
        elif not pr.origin or procurement.origin not in pr.origin.split(", "):
            if pr.origin:
                if procurement.origin:
                    pr.write({"origin": pr.origin + ", " + procurement.origin})
                else:
                    pr.write({"origin": pr.origin})
            else:
                pr.write({"origin": procurement.origin})
        # Create Line
        request_line_data = rule._prepare_purchase_request_line(pr, procurement)
        # check if request has lines for same product and data
        # if yes, update qty instead of creating new line
        same_product_date_request_line = pr.line_ids.filtered_domain(
            [
                ("product_id", "=", request_line_data["product_id"]),
                ("date_required", "=", request_line_data["date_required"].date()),
                (
                    "purchase_state",
                    "=",
                    False,
                ),  # avoid updating if there is RFQ or PO linked
            ],
        )
        if same_product_date_request_line:
            new_product_qty = (
                same_product_date_request_line.product_qty
                + request_line_data["product_qty"]
            )
            same_product_date_request_line.write({"product_qty": new_product_qty})
        else:
            # Create Line
            purchase_request_line_model.create(request_line_data)
